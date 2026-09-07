# [C] NASA AIT-Core vulnerable to SQL Injection

## Summary
Severity: Critical
Advisory: GHSA-gpgj-xrgw-8mx2
CVE: CVE-2024-35056
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-21
Source: https://github.com/advisories/GHSA-gpgj-xrgw-8mx2
Type: github-advisory

## Affected
- PyPI: `ait-core` — affected >=0

## Details
NASA AIT-Core v2.5.2 was discovered to contain multiple SQL injection vulnerabilities via the `query_packets` and `insert` functions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-35056
- https://github.com/NASA-AMMOS/AIT-Core/issues/527
- https://github.com/NASA-AMMOS/AIT-Core
- https://www.linkedin.com/pulse/remote-code-execution-via-man-in-the-middle-more-ujkze
