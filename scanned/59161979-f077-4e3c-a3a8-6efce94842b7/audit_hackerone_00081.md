# [M] HTTP Request Smuggling via Empty headers separated by CR

## Summary
Severity: Medium
Program: Node.js
Weakness: HTTP Request Smuggling
Reporter: yadhukrishnam
State: resolved
Disclosed: 2023-06-20T21:04:25.574Z
CVE: CVE-2023-30589
Source: https://hackerone.com/reports/2001873

## Details
**Summary:** 
The `llhttp` parser in the http module in Node v20.2.0 does not strictly use the CRLF sequence to delimit HTTP requests. This can lead to HTTP Request Smuggling (HRS).

**Description:** 
The CR character (without LF) is sufficient to delimit HTTP header fields in the llhttp parser. According to RFC7230 section 3, only the CRLF sequence should delimit each header-field.

## Steps To Reproduce:

*Server:*

```javascript
const http = require("http");

http
  .createServer((request, response) => {
    let body = [];
    request
      .on("error", (err) => {
        response.end("Request Error: " + err);
      })
      .on("data", (chunk) => {
        body.push(chunk);
      })
      .on("end", () => {
        body = Buffer.concat(body).toString();

        // log the body to stdout to catch the smuggled request
        console.log("Response");
        console.log(request.headers);
        console.log(body);
        console.log("---");

        response.on("error", (err) => {
          // log the body to stdout to catch the smuggled request
          response.end("Response Error: " + err);
        });

        response.end(
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/2001873_
