import sys
from os import path
from PIL import Image


# the "pallete" of ascii characters used - from lowest to highest intensity
ASCII_CHARS = [' ','.',',',':',';','+','*','?','%','S','#','@']
DEFAULT_WIDTH = 70


# resize an image while keeping the aspect ratio constant
def resize(image, new_width):
	(old_width, old_height) = image.size
	aspect_ratio = old_height / old_width
	new_height = int(aspect_ratio * new_width)
	new_dim = (new_width, new_height)
	new_image = image.resize(new_dim)
	return new_image


# turn 1 gif frame into ascii art
def asciify_gif_frame(frame, charwidth):
	frame = resize(frame, charwidth).convert('L')
	bw_pixels = list(frame.getdata())
	
	ascii_pixels = [ASCII_CHARS[min(pixel * len(ASCII_CHARS) // 255, len(ASCII_CHARS)-1)] for pixel in bw_pixels]
	ascii_pixels = ''.join(ascii_pixels)

	ascii_frame = [ascii_pixels[index:index+charwidth] for index in range(0, len(ascii_pixels), charwidth)]
	return '\n'.join(ascii_frame)


# replace some special .bat characters with their escaped versions..
def escape_bat(string):
	return string.replace('%', '%%').replace('^', '^^').replace('&', '^&').replace('<', '^<').replace('>', '^>').replace('|', '^|')
	
	
# write a header that appears before anything else in the batch file
def write_bat_header(bat, title, width, height):
	bat.write(f'::--------------------------------------------------------::\n')
	bat.write(f':: This file was generated by asciify.py from {title}.gif ::\n')
	bat.write(f':: See https://github.com/blat-blatnik/asciify            ::\n')
	bat.write(f'::--------------------------------------------------------::\n')
	bat.write(f'@echo off\n')                               # don't print out every command
	bat.write(f'mode con:cols={width} lines={height+2}\n')  # set width and height of the console
	bat.write(f'title {title}\n')                           # set the title
	bat.write(f':: uncomment the line below to change the colors\n')
	bat.write(f'::color BC\n')
	bat.write(f'echo \x1B[?25l\n')                          # turn off the cursor
	bat.write(f':start\n')                                  # set a label to jump back to for looping the animation
	
	
# write out a single frame of the batch ascii art animation
def write_bat_frame(bat, frame):
	for line in frame.split('\n'):
		if line.strip() == '':
			bat.write(f'echo.\n')
		else:
			bat.write(f'echo {escape_bat(line)}\n')
	bat.write(f'echo \x1B[H\n') # put cursor in top-left
	bat.write(f'call :Wait\n')  # call the wait routine so animation isn't too fast
	
	
# write out the batch footer which apears after everything else in the file
def write_bat_footer(bat, waittime):
	bat.write(f'goto :start\n')          # loop the animation
	# write out a 'Wait' procedure which just pings
	# localhost in a loop..
	bat.write(f':: wait routine - you can add/remove some ping lines to make the animation faster or slower\n')
	bat.write(f':Wait\n')
	for i in range(waittime):
		bat.write(f'::ping localhost -n 1 >nul\n')
	bat.write(f'exit /B 0\n') # return to caller
	

# convert the whole gif image into an ascii animation
def asciify_gif(gif, outfile, outname, charwidth=80):
	with open(outfile, 'w') as bat:	
		frame = Image.open(gif)
		nframes = 0
		
		while frame:
			ascii_frame = asciify_gif_frame(frame, charwidth)
			print(ascii_frame)
			
			if nframes == 0:
				write_bat_header(bat, outname, charwidth, len(ascii_frame.split('\n')))
			write_bat_frame(bat, ascii_frame)
			
			nframes += 1
			try:
				frame.seek(nframes)
			except EOFError:
				break;
				
		write_bat_footer(bat, 1)
				
	
def print_usage():
	print(f'asciify: convert a .gif file into an animated ascii batch file')
	print(f'usage: $ python3 {sys.argv[0]} gif [width={DEFAULT_WIDTH}]')
	print(f' gif   - input gif file')
	print(f' width - width in characters of the ascii animation')
	
	
if __name__ == '__main__':
	argc = len(sys.argv)
	charwidth = DEFAULT_WIDTH
	
	if argc < 2 or argc > 3:
		print_usage()
		exit()
	if argc == 3:
		charwidth = int(sys.argv[2])

	gif = sys.argv[1]
	filename, extension = path.splitext(path.basename(gif))
	#if extension != '.gif':
	#	print(f"ERROR: '{gif}' is not a gif file .. exiting")
	#	exit()
	
	outfile = filename + '.bat'
	asciify_gif(gif, outfile, filename, charwidth)