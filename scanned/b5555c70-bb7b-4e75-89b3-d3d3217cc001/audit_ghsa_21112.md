# [M] undici before v5.8.0 vulnerable to CRLF injection in request headers

## Summary
Severity: Medium
Advisory: GHSA-3cvr-822r-rqcc
CVE: CVE-2022-31150
CWE: CWE-93
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-07-21
Source: https://github.com/advisories/GHSA-3cvr-822r-rqcc
Type: github-advisory

## Affected
- npm: `undici` — affected >=0 <5.8.0

## Details
### Impact

It is possible to inject CRLF sequences into request headers in Undici.

```js
const undici = require('undici')

const response = undici.request("http://127.0.0.1:1000", {
  headers: {'a': "\r\nb"}
})
```

The same applies to `path` and `method`

### Patches

Update to v5.8.0

### Workarounds

Sanitize all HTTP headers from untrusted sources to eliminate `\r\n`.

### References

https://hackerone.com/reports/409943
https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-12116

### For more information

If you have any questions or comments about this advisory:

* Open an issue in [undici repository](https://github.com/nodejs/undici/issues)
* To make a report, follow the [SECURITY](https://github.com/nodejs/node/blob/HEAD/SECURITY.md) document

## References
- https://github.com/nodejs/undici/security/advisories/GHSA-3cvr-822r-rqcc
- https://nvd.nist.gov/vuln/detail/CVE-2022-31150
- https://github.com/nodejs/undici/commit/a29a151d0140d095742d21a004023d024fe93259
- https://hackerone.com/reports/409943
- https://github.com/nodejs/undici
- https://github.com/nodejs/undici/releases/tag/v5.8.0
- https://security.netapp.com/advisory/ntap-20220915-0002
