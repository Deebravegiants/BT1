# [H] NASA AIT-Core uses unencrypted channels to exchange data over the network

## Summary
Severity: High
Advisory: GHSA-qv6x-53jj-vw59
CVE: CVE-2024-35061
CWE: CWE-311
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-05-21
Source: https://github.com/advisories/GHSA-qv6x-53jj-vw59
Type: github-advisory

## Affected
- PyPI: `ait-core` — affected >=0

## Details
NASA AIT-Core v2.5.2 was discovered to use unencrypted channels to exchange data over the network, allowing attackers to execute a man-in-the-middle attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-35061
- https://github.com/NASA-AMMOS/AIT-Core
- https://www.linkedin.com/pulse/remote-code-execution-via-man-in-the-middle-more-ujkze
