### What is it?
It is a simple lambda function that can help you to automate of suspicious domains checking. Domains that an attacker 
may use for a spear-phishing campaign. The function just check DNS records and notify you as soon as a domain from a list 
is registered.

Take a look at `template.yaml` file, you can use it to simply and fast deploy the function in your AWS account.
Also, the file is accessible from `https://s3.eu-central-1.amazonaws.com/securityblog.cloud/cf_files/template.yaml`
### After deployment
Go to deployed lambda function and
* specify SNS Topic in environment variables
* add domains name you want to check in the list (default: domains.txt). You may use [dnstwist](https://github.com/elceef/dnstwist). 