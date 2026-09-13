# [H] Alkacon OpenCms allows remote unauthenticated attackers to obtain sensitive information

## Summary
Severity: High
Advisory: GHSA-rcc6-6q2f-m2cw
CVE: CVE-2023-42344
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-rcc6-6q2f-m2cw
Type: github-advisory

## Affected
- Maven: `org.opencms:opencms-core` — affected >=0 <10.5.1

## Details
Alkacon OpenCms before 10.5.1 allows remote unauthenticated attackers to obtain sensitive information via a cmis-online/query XXE attack on a Chemistry servlet.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-42344
- https://github.com/projectdiscovery/nuclei-templates/issues/8864
- https://github.com/alkacon/opencms-core
- https://labs.watchtowr.com/xxe-you-can-depend-on-me-opencms
