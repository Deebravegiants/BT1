# [M] SiYuan before v3.8.2 Information Disclosure via Attribute-View

## Summary
Severity: Medium
Advisory: CVE-2026-86192
Aliases: GHSA-vc7j-5f5p-3x75
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-05
Source: https://osv.dev/vulnerability/CVE-2026-86192
Type: osv

## Details
SiYuan versions before v3.8.2 fail to properly filter private attribute-view cell values in the getAttributeViewKeys endpoint. Publish readers can retrieve hidden KeyValues payloads from rows bound to inaccessible documents, exposing private database contents without authorization.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86192.json
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-vc7j-5f5p-3x75
- https://nvd.nist.gov/vuln/detail/CVE-2026-86192
- https://www.vulncheck.com/advisories/siyuan-before-3.8.2-information-disclosure-via-attribute-view
