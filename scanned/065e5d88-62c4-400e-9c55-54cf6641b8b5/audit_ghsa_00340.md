# [C] Denial of Service in memjs

## Summary
Severity: Critical
Advisory: GHSA-cx8m-8xmx-q8v3
CVE: CVE-2018-3767
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2018-10-10
Source: https://github.com/advisories/GHSA-cx8m-8xmx-q8v3
Type: github-advisory

## Affected
- npm: `memjs` — affected >=0

## Details
Versions of `memjs` prior to 1.2.2 are vulnerable to Denial of Service (DoS).  The package fails to sanitize the `value` option passed to the Buffer constructor, which may allow attackers to pass large values exhausting system resources.


## Recommendation

Upgrade to version 1.2.2 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3767
- https://hackerone.com/reports/319809
- https://github.com/advisories/GHSA-cx8m-8xmx-q8v3
- https://www.npmjs.com/advisories/970
