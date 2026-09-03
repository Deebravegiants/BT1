# [M] [m-server] Path Traversal allows to display content of arbitrary file(s) from the server

## Summary
Severity: Medium (CVSS 6.1)
Program: Node.js third-party modules
Weakness: Path Traversal
Reporter: bl4de
State: resolved
Disclosed: 2018-07-12T08:41:18.156Z
CVE: CVE-2018-16485
Source: https://hackerone.com/reports/319795

## Details
I would like to report Path Traversal in ```m-server``` module.
It allows to read content of any arbitrary file from the server where ```m-server``` is installed and run.

## Module

**module name:** m-server
**version:** 1.4.0
**npm page:** https://www.npmjs.com/package/m-server

### Module Description

M-Server is a mini http static server that without any dependencies;

### Module Stats

Stats
6 downloads in the last day
68 downloads in the last week
180 downloads in the last month

~2200 estimated downloads per year

## Vulnerability Description

Path Traversal vulnerability in m-server module allows to go up in directory tree and read content of any file, like ```/etc/passwd```

Vulnerability exists, because ```m-server``` does not implement any protection against Path Traversal attacks and use provided path as-is:

```javascript
// node_modules/m-server/lib/index.js, line 10

    var targetPath = path.join(rootPath, req.url);
    if (fs.existsSync(targetPath)) {
        var targetType = fs.lstatSync(targetPath);
        if (targetType.isFile()) {
            res.end(fs.readFileSync(targetPath))   // <-- vulnerable code
        } else if (targetType.isDirectory()) {
            
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/319795_
