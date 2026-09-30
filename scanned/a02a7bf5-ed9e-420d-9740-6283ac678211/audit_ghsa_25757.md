# [M] Exposure of Sensitive information in httpie

## Summary
Severity: Medium
Advisory: GHSA-6pc9-xqrg-wfqw
CVE: CVE-2022-0430
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:R/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-03-16
Source: https://github.com/advisories/GHSA-6pc9-xqrg-wfqw
Type: github-advisory

## Affected
- PyPI: `httpie` — affected >=0 <3.1.0

## Details
httpie is a modern, user-friendly command-line HTTP client for the API era. Prior to version 3.1.0, all cookies saved to session storage are supercookies. At this time, there is no known workaround. Users are recommended to update to version 3.1.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0430
- https://github.com/httpie/httpie/commit/65ab7d5caaaf2f95e61f9dd65441801c2ddee38b
- https://github.com/advisories/GHSA-6pc9-xqrg-wfqw
- https://github.com/httpie/httpie
- https://github.com/pypa/advisory-database/tree/main/vulns/httpie/PYSEC-2022-167.yaml
- https://huntr.dev/bounties/dafb2e4f-c6b6-4768-8ef5-b396cd6a801f
