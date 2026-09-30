# [H] pdfmake is vulnerable to server-side request forgery (SSRF)

## Summary
Severity: High
Advisory: GHSA-wp52-r2fp-4vmr
CVE: CVE-2026-26801
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-10
Source: https://github.com/advisories/GHSA-wp52-r2fp-4vmr
Type: github-advisory

## Affected
- npm: `pdfmake` — affected >=0.3.0-beta.2 <0.3.6

## Details
Server-Side Request Forgery (SSRF) vulnerability in pdfmake versions 0.3.0-beta.2 through 0.3.5 allows a remote attacker to obtain sensitive information via the src/URLResolver.js component. The fix was released in version 0.3.6 which introduces the setUrlAccessPolicy() method allowing server operators to define URL access rules. A warning is now logged when pdfmake is used server-side without a policy configured.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-26801
- https://github.com/bpampuch/pdfmake/pull/2920
- https://github.com/bpampuch/pdfmake
- https://github.com/bpampuch/pdfmake/blob/master/src/URLResolver.js
- https://github.com/bpampuch/pdfmake/releases/tag/0.3.6
- https://mariopepe.github.io/cve-2026-26801-pdfmake-ssrf
