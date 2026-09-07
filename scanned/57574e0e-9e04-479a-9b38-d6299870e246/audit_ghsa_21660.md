# [M] url-parse incorrectly parses hostname / protocol due to unstripped leading control characters.

## Summary
Severity: Medium
Advisory: GHSA-jf5r-8hm2-f872
CVE: CVE-2022-0691
CWE: CWE-639
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-02-22
Source: https://github.com/advisories/GHSA-jf5r-8hm2-f872
Type: github-advisory

## Affected
- npm: `url-parse` — affected >=0.1.0 <1.5.9

## Details
Leading control characters in a URL are not stripped when passed into url-parse. This can cause input URLs to be mistakenly be interpreted as a relative URL without a hostname and protocol, while the WHATWG URL parser will trim control characters and treat it as an absolute URL.

If url-parse is used in security decisions involving the hostname / protocol, and the input URL is used in a client which uses the WHATWG URL parser, the decision may be incorrect.

This can also lead to a cross-site scripting (XSS) vulnerability if url-parse is used to check for the javascript: protocol in URLs. See following example:
```js
const parse = require('url-parse')
const express = require('express')
const app = express()
const port = 3000

url = parse(\"\\bjavascript:alert(1)\")

console.log(url)

app.get('/', (req, res) => {
 if (url.protocol !== \"javascript:\") {res.send(\"<a href=\\'\" + url.href + \"\\'>CLICK ME!</a>\")}
 })

app.listen(port, () => {
 console.log(`Example app listening on port ${port}`)
 })
```

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0691
- https://github.com/github/advisory-database/pull/6765
- https://github.com/unshiftio/url-parse/commit/0e3fb542d60ddbf6933f22eb9b1e06e25eaa5b63
- https://github.com/unshiftio/url-parse
- https://huntr.dev/bounties/57124ed5-4b68-4934-8325-2c546257f2e4
- https://lists.debian.org/debian-lts-announce/2023/02/msg00030.html
- https://security.netapp.com/advisory/ntap-20220325-0006
