# [M] `undici.request` vulnerable to SSRF using absolute URL on `pathname`

## Summary
Severity: Medium
Advisory: GHSA-8qr4-xgw6-wmr3
CVE: CVE-2022-35949
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-08-18
Source: https://github.com/advisories/GHSA-8qr4-xgw6-wmr3
Type: github-advisory

## Affected
- npm: `undici` — affected >=0 <5.8.2

## Details
### Impact

`undici` is vulnerable to SSRF (Server-side Request Forgery) when an application takes in **user input** into the `path/pathname` option of `undici.request`.

If a user specifies a URL such as `http://127.0.0.1` or `//127.0.0.1`

```js
const undici = require("undici")
undici.request({origin: "http://example.com", pathname: "//127.0.0.1"})
```

Instead of processing the request as `http://example.org//127.0.0.1` (or `http://example.org/http://127.0.0.1` when `http://127.0.0.1 is used`), it actually processes the request as `http://127.0.0.1/` and sends it to `http://127.0.0.1`.

If a developer passes in user input into `path` parameter of `undici.request`, it can result in an _SSRF_ as they will assume that the hostname cannot change, when in actual fact it can change because the specified path parameter is combined with the base URL.

### Patches

This issue was fixed in `undici@5.8.1`.

### Workarounds

The best workaround is to validate user input before passing it to the `undici.request` call.

## For more information
If you have any questions or comments about this advisory:

- Open an issue in [undici repository](https://github.com/nodejs/undici/issues)
- To make a report, follow the [SECURITY](https://github.com/nodejs/node/blob/HEAD/SECURITY.md) document

## References
- https://github.com/nodejs/undici/security/advisories/GHSA-8qr4-xgw6-wmr3
- https://nvd.nist.gov/vuln/detail/CVE-2022-35949
- https://github.com/nodejs/undici/commit/124f7ebf705366b2e1844dff721928d270f87895
- https://github.com/nodejs/undici
- https://github.com/nodejs/undici/releases/tag/v5.8.2
