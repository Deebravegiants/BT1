# [C] [html-pages] Path Traversal in html-pages module allows to read any file from the server with curl

## Summary
Severity: Critical (CVSS 9.5)
Program: Node.js third-party modules
Weakness: Path Traversal
Reporter: bl4de
State: resolved
Disclosed: 2018-05-19T12:55:48.532Z
CVE: CVE-2018-3744
Source: https://hackerone.com/reports/306607

## Details
Hi,

This report is about Directory Traversal vulnerability I found in ```html-pages``` module.


**Module:** 

html-pages is a module which allows to browse directories and  serve static files in the browser. The vulnerability exists in the latest available version (2.0.7)

Link to npm page: https://www.npmjs.com/package/html-pages

**Summary:** 

When html-pages server is run, browser does not allow toread files from arbitrary locations. However, I've noticed that using simple bypasses with ```%2e``` (.) or ```%2f``` (/) I can easily go up in the directory tree. 
But it's not possible to open any file in the browser, due to characters used in the path, only directory listing is available:

{F255390}


However, with simple ```curl``` call we can read any file on the remote server where ```html-pages``` runs:

```
$ curl -v --path-as-is http://localhost:8000/../../../../../Users/bl4de/.vimrc
```

{F255392}

Here is the part of the code, which read directory content, but does not validate against Directory Traversal in any way, which literally makes ```root``` config setting useless:

https://github.com/danielcardoso/html-pages/blob/master/lib/server.js#L122


This vulnerability can be exploited regardless of some ```html-pages``` configuration settings, like ```root```. All files on the server can be read by malicious user.


## Steps To Reproduce:

- install ```html-pages```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/306607_
