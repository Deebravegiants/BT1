# [H] [mcstatic] Path Traversal allows to read content of arbitrary files

## Summary
Severity: High (CVSS 8.6)
Program: Node.js third-party modules
Weakness: Path Traversal
Reporter: bl4de
State: resolved
Disclosed: 2018-04-24T19:46:53.316Z
CVE: CVE-2018-3730
Source: https://hackerone.com/reports/312907

## Details
Hi Guys,

There is Path Traversal in mcstatic module.
It allows to read content of arbitrary files on the remote server.

## Module

**mcstatic**

This is a general file server made by nodejs. It will be easy for you to access the files on the server through the browser.

https://www.npmjs.com/package/mcstatic

version: 0.0.20

Stats
0 downloads in the last day
38 downloads in the last week
150 downloads in the last month

~1800 estimated downloads per year


## Description

Lack of file path sanitization causes that any file on the server might be read by malicious user.

If we follow code flow, we find that first file name is read from ```req.url``` and check if exists:

```javascript
// node_modules/mcstatic/lib/staticFileHandler.js, line 19:
    var filePath = httpHelpers.getRequestPathFromUrl(req.url);
    var mockedFilePath = findMockFilePath(filePath,mockPaths);
    if(mockedFilePath)
        filePath = mockedFilePath;

    var file = path.normalize(path.join(root,filePath));
    fs.stat(file,function(error, stats){
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/312907_
