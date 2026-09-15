# [H] Aim Excessive Data Query Operations in a Large Data Table vulnerability

## Summary
Severity: High
Advisory: GHSA-fm93-g6xp-35xq
CVE: CVE-2025-0190
CWE: CWE-1049
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-fm93-g6xp-35xq
Type: github-advisory

## Affected
- PyPI: `aim` — affected >=0

## Details
In version 3.25.0 of aimhubio/aim, a denial of service vulnerability exists. By tracking a large number of `Text` objects and then querying them simultaneously through the web API, the Aim web server becomes unresponsive to other requests for an extended period while processing and returning these objects. This vulnerability can be exploited repeatedly, leading to a complete denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-0190
- https://github.com/aimhubio/aim
- https://huntr.com/bounties/38d151f1-abb4-443a-86b0-6c26f0c6cb70
