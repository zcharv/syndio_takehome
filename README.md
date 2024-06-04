## Usage

To start the api, please use the following cli command where ```some_port``` is any port you want the api to be served on.
Once the api has started, please navigate to ```http://localhost:some_port/pvalue/Engineering```. The 'Engineering' 
parameter is filtering by employee department, however Engineering is the only department currently in the db.

```bash
make PORT={some_port} start
```