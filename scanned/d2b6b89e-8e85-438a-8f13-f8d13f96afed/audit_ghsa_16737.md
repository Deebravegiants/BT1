# [C] NASA AIT-Core vulnerable to remote code execution

## Summary
Severity: Critical
Advisory: GHSA-4gxj-5mmr-7pxq
CVE: CVE-2024-35058
CWE: CWE-319
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-21
Source: https://github.com/advisories/GHSA-4gxj-5mmr-7pxq
Type: github-advisory

## Affected
- PyPI: `ait-core` — affected >=0

## Details
An issue in the API wait function of NASA AIT-Core v2.5.2 allows attackers to execute arbitrary code via supplying a crafted string.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-35058
- https://github.com/NASA-AMMOS/AIT-Core/issues/528
- https://github.com/NASA-AMMOS/AIT-Core
- https://www.linkedin.com/pulse/remote-code-execution-via-man-in-the-middle-more-ujkze
