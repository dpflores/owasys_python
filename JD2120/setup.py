import os

def main():
	print("Instalando dependencias")

	os.system("apt-get install libatlas-base-dev")
	os.system("pip3 install -r requirements.txt")

	print("Hecho")
if __name__ == '__main__':
	main()