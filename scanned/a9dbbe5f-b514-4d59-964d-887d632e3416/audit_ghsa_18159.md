# [H] Finance.js vulnerable to DoS via the IRR function’s depth parameter

## Summary
Severity: High
Advisory: GHSA-f8r4-mf27-rf7m
CVE: CVE-2025-56571
CWE: CWE-400, CWE-770, CWE-834
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-09-30
Source: https://github.com/advisories/GHSA-f8r4-mf27-rf7m
Type: github-advisory

## Affected
- npm: `financejs` — affected >=0

## Details
Finance.js v4.1.0 contains a Denial of Service (DoS) vulnerability via the IRR function’s depth parameter. Improper handling of the recursion/iteration limit can lead to excessive CPU usage, causing application stalls or crashes.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-56571
- https://github.com/ebradyjobory/finance.js
- https://medium.com/@nakah_/cve-2025-56571-and-cve-2025-56572-denial-of-service-vulnerabilities-in-finance-js-78f8b399f53b
- https://raw.githack.com/ebradyjobory/finance.js/6d571ea2a86d08491ceb584e292e9b76b0a60636/finance.js
- http://financejs.com
