# DT5202 Data Fixer

The DT5202 Data Fixer is a tiny python script that fixes the data from the CAEN DT5202. It will detect frame-wise flaws in the original data file and try to sort them out. Typically four types of flaws are detected:

 - Incorrect TrgID
 - Incorrect TS
 - Incorrect CH Value
 - Incomplete Frame

Please note that the underlying causes of these flaws are not fully understood and may be addressed by CAEN in the future. Use this script only if you are certain of its necessity, and always verify the data after applying the fix.

## Requirements

* Python 3.10 (other versions are untested)
* Requires the following python modules:
    * numpy
    * argparse
    * matplotlib
    * collections
    * time

## Usage

1. Clone the repository

2. Install required libraries or packages (if any):

3. Run with command line 

    ```bash
        python DT5202_Data_Fixer.py --input <input_file> -output <output_file>
    ```

    - The `--output` argument is optional. If not specified, the script will only check the data without generating a fixed file.

4. (Optional) Running with bash script
   
   - An example bash script, `example_bash_script.sh`, is provided to demonstrate how to process multiple files at once.
    
## Testing

The fixer is only tested on MacOS with python 3.10. Other platforms and python versions are not tested. But it should work as no platform specific code is used.

## License

[MIT](https://choosealicense.com/licenses/mit/)

## Responsibility

This script is provided "as is" without warranty of any kind, either express or implied. By using this script, you agree that you are solely responsible for any consequences that may arise from its use. The author is not responsible for any damage, loss of data, or any other issues that may occur as a result of using this script. Please use it responsibly and at your own risk.