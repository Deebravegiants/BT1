# [H] HuTool XML parsing module has blind XXE vulnerability

## Summary
Severity: High
Advisory: GHSA-p2qf-9vp6-3jjq
CVE: CVE-2023-3276
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-06-15
Source: https://github.com/advisories/GHSA-p2qf-9vp6-3jjq
Type: github-advisory

## Affected
- Maven: `cn.hutool:hutool-core` — affected >=0

## Details
A vulnerability, which was classified as problematic, has been found in Dromara HuTool up to 5.8.19. Affected by this issue is the function readBySax of the file XmlUtil.java of the component XML Parsing Module. The manipulation leads to xml external entity reference.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-3276
- https://fbdhhhh47.github.io/2023/06/06/hutool-XXE
- https://github.com/dromara/hutool
- https://vuldb.com/?ctiid.231626
- https://vuldb.com/?id.231626
