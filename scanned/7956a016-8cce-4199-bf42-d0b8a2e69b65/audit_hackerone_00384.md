# [M] [crud-file-server] Path Traversal allows to read arbitrary file from the server

## Summary
Severity: Medium
Program: Node.js third-party modules
Weakness: Path Traversal
Reporter: bl4de
State: resolved
Disclosed: 2018-04-03T23:04:07.517Z
CVE: CVE-2018-3733
Source: https://hackerone.com/reports/310690

## Details
Hi Guys,

There is Path Traversal vulnerability in crud-file-server module, which allows to read arbitrary file from the remote server.

## Module

**crud-file-server**

This package exposes a directory and its children to create, read, update, and delete operations over http.

https://www.npmjs.com/package/crud-file-server

version: 0.7.0

Stats
0 downloads in the last day
26 downloads in the last week
220 downloads in the last month

~2500 estimated downloads per year


## Description

This vulnerability is caused by simple mistake in function which should block Path Traversal attempts:


```javascript
// ./node_modules/crud-file-server/crud-file-server.js, line 4:
var cleanUrl = function(url) { 
	url = decodeURIComponent(url);
	while(url.indexOf('..').length > 0) { url = url.replace('..', ''); }
	return url;
};
```

As you can see, condition which checks existence of ```..``` is wrong, because ```url.indexOf()``` returns index of found string or -1 if nothing matches; and has no ```length``` property. Because of that, this condition is always false, thus ```url = url.replace('..', '');``` is never executed.


_Trimmed to 38 lines — full report: https://hackerone.com/reports/310690_
