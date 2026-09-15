# [M] Suricata: Stack buffer overflow in rule parser when processing long keywords with transforms

## Summary
Severity: Medium
Advisory: CVE-2025-59149
Aliases: GHSA-vxcg-38x4-gj7j
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2025-59149
Type: osv

## Details
Suricata is a network IDS, IPS and NSM engine developed by the OISF (Open Information Security Foundation) and the Suricata community. In version 8.0.0, rules using keyword ldap.responses.attribute_type (which is long) with transforms can lead to a stack buffer overflow during Suricata startup or during a rule reload. This issue is fixed in version 8.0.1. To workaround this issue, users can disable rules with ldap.responses.attribute_type and transforms.

## References
- https://forum.suricata.io/t/suricata-8-0-1-and-7-0-12-released/6018
- https://redmine.openinfosecfoundation.org/issues/7861
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59149.json
- https://github.com/OISF/suricata/security/advisories/GHSA-vxcg-38x4-gj7j
- https://nvd.nist.gov/vuln/detail/CVE-2025-59149
- https://github.com/OISF/suricata/commit/38a2cba5c397002047d84645f5ab770ff88020e1
