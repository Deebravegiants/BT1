# [H] [public] Path Traversal allows to read content of arbitrary files

## Summary
Severity: High (CVSS 8.6)
Program: Node.js third-party modules
Weakness: Path Traversal
Reporter: bl4de
State: resolved
Disclosed: 2018-02-17T17:44:13.493Z
CVE: CVE-2018-3731
Source: https://hackerone.com/reports/312918

## Details
Hi Guys,

There is Path Traversal in public module.
It allows to read content of arbitrary files on the remote server.

## Module

**public**

Run static file hosting server with specified public dir & port. Support a "direcotry index" like Apache httpd.

https://www.npmjs.com/package/public

version: 0.1.2

Stats
3 downloads in the last day
30 downloads in the last week
384 downloads in the last month

~4600 estimated downloads per year


## Description

Lack of file path sanitization causes that any file on the server might be read by malicious user.

Vulnerability exists, because path is used without any check against Path Traversal attacks:

```javascript
// node_modules/public/bin/public, line 73:
    var pathname = url.parse(req.url).pathname;
    var filePath = path.join(dir, pathname); // Real file path
    var base = filePath.replace(dir, ''); // Base path for browser link
    var abs = path.resolve(filePath); 
    console.log(new Date().toString(), abs);
    fs.readFile(filePath, function(err, data) {
      if (err) {
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/312918_
