# [M] [bruteser] Path Traversal allows to read content of arbitrary file

## Summary
Severity: Medium (CVSS 6.5)
Program: Node.js third-party modules
Weakness: Path Traversal
Reporter: bl4de
State: resolved
Disclosed: 2018-07-04T19:41:30.036Z
Source: https://hackerone.com/reports/342066

## Details
I would like to report Path Traversal in ```bruteser``` module.
It allows to read content of any arbitrary file from the server where ```bruteser``` is installed and run.

## Module

**module name:** bruteser
**version:** 0.0.2
**npm page:** https://www.npmjs.com/package/bruteser

### Module Description

BruteSer - server can be used for any type of static files. Just put your files to "public" folder, run server.js and access localhost:8080/your_file.html

If type localhost:8080 it will run index.html by default

### Module Stats

N/A, this module is new and rarely used, but I just wanted maintainer to be aware of the issue as the module is available in public npm directory.

## Vulnerability Description

Path Traversal vulnerability in bruteser module allows to go up in directory tree and read content of any file, like ```/etc/passwd```

Vulnerability exists, because ```bruteser``` uses variable ```filepath``` without any protection against Path Traversal attacks:

```javascript
// node_modules/bruteser/server.js, line 8 (some lines removed)


	var filepath = req.url;
	if (filepath=='/') {
		var filepath = '/index.html';
	}

	var ext = path.extname(filepath);

    // REMOVED

```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/342066_
