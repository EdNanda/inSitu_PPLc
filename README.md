# inSitu_PPLc
Graphical interface that allows the simultaneous collection of data coming from a Pressure sensor, PL spectrometer, and camera.

## Description
This program creates graphical interface using tkinter that allows the simultaenous collection of pressure data from a Thyracont sensor, PL spectra from an Ocean Optics spectrometer, and images from a usb camera.

This program was used to collect the data shown in the Material Advances publication [DOI:10.1039/D1MA00494H] https://doi.org/10.1039/D1MA00494H 

## Installation
Please install the libraries shown in the requirements.txt

## Usage
When starting the program, a windows will appear asking about the sensors that want the be used. After that, a live feed of the selected sensors will be shown. It is possible to run the program without sensors. 

It is recommended to fill up the numerous metadata fields for future analysis.

A measurement can be started by pressing the start button.

Once the measurement is done, a folder will be created with the name of the sample and it will contain CSV files for the pressure vs time, PL vs time, and a folder containing photo frames with the timestamp in the filename, depending what sensors where selected.


## Support
For help, contact enandayapa@gmail.com

## Roadmap
The program is on a finished state, albeit some small bugs that might need fixing. 
Please contact us if you find any new issues.

[Spectra Compiler] (https://gitlab.hzdr.de/hyd/spectra-compiler.git) was created as an improved version of this program, although it does not allow for the simultaneous collection of pressure nor photoframes. The new program uses a parallel thread to make the program more functional during the measurement process.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## Authors and acknowledgment
All programming was done by Edgar Nandayapa B.
Field testing has been done by C. Rehermann and F. Mathies.

## License
[MIT](https://choosealicense.com/licenses/mit/)

## Known issues
No known issues