# [M] CVE-2024-50615

## Summary
Severity: Medium
Advisory: CVE-2024-50615
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2024-10-27
Source: https://osv.dev/vulnerability/CVE-2024-50615
Type: osv

## Details
TinyXML2 through 10.0.0 has a reachable assertion for UINT_MAX/digit, that may lead to application exit, in tinyxml2.cpp XMLUtil::GetCharacterRef.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50615.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50615
- https://github.com/leethomason/tinyxml2/issues/997
