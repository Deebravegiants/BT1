# [H] Denial of Service via malformed accept-encoding header in hapi

## Summary
Severity: High
Advisory: GHSA-cqjg-whmm-8gv6
CVE: CVE-2017-16013
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-10-09
Source: https://github.com/advisories/GHSA-cqjg-whmm-8gv6
Type: github-advisory

## Affected
- npm: `hapi` — affected >=15.0.0 <16.1.1

## Details
Affected versions of `hapi` will crash or lock the event loop when a malformed `accept-encoding` header is recieved.


## Recommendation

Update to version 16.1.1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16013
- https://github.com/hapijs/hapi/issues/3466
- https://github.com/advisories/GHSA-cqjg-whmm-8gv6
- https://www.npmjs.com/advisories/335
