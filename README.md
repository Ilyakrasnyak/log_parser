Utility for parsing logs. 

python log_parser.py -f <path_to_file> -s <path_to_result>

    -f, --file
        if the argument is a file - processes it
        if the argument is a directory - processes all files in the directory
    -s, --save_to
        if the argument is specified - saves the result on the specified path.
        otherwise saves the result in the current directory like 'result.json'

The result file contains:
- The total number of collected requests
- Number of requests of the following types: GET - 20, POST - 10, etc.
- Top 10 IP addresses from which requests were made
- Top 10 longest requests
- Top 10 requests that ended with a client error
- Top 10 requests which ended with an error on the server side
- All lines which invoked error while parsing
