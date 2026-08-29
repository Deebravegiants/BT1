# [M] HTTP Request Smuggling via Content Length Obfuscation

## Summary
Severity: Medium (CVSS 6.5)
Program: Node.js
Weakness: HTTP Request Smuggling
Reporter: bpingel
State: resolved
Disclosed: 2024-05-03T14:55:56.399Z
CVE: CVE-2024-27982
Source: https://hackerone.com/reports/2237099

## Details
**Summary:** The default web service in the most recent version of 18.X seems to have an issue with the interpretation of malformed headers. If a space is left before a content-length header then the header is not read correctly. This leaves the ability to smuggle in a second request as the body of the first.

**Description:** HTTP request smuggling is present in applications running on the current version of the 18.X Node JS available for download from nodejs.org. When a space is placed before the content length header of a request it is not interpreted correctly and as a result the beginning of another request can be smuggled in the body. Formatted correctly it can consume portions of other user's requests or force them to access paths they did not intend to.

## Steps To Reproduce:

This simple Node JS application was used for replication and showing of desync in identification parameters within requests.

```
const http = require('http');
const port = 8082;

const server = http.createServer((req, res) => {
  if (req.url === '/hello') {
    console.log(JSON.stringify(req.headers));
    console.log('%s', req.url);
    res.writeHead(200, { 'Content-Type': 'text/plain' });
    res.end('Hello, World!\n');
  } else if (req.url === '/bye') {
    console.log('%s', req.url)
    console.log(JSON.stringify(req.headers));
    res.writeHead(200, { 'Content-Type': 'text/plain' });
    const name = req.headers['x-name'] || 'World';
    res.end(`Goodbye, ${name}!\n`);
  } else {
    res.writeHead(404, { 'Content-Type': 'text/plain' });
    res.end('Route not found\n');
  }
});

server.listen(port, () => {
  console.log(`Server running at http://localhost:${port}/`);
});
```
and the smuggled request would look like this
```
POST /hello HTTP/1.1
Host: 127.0.0.1
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/2237099_
