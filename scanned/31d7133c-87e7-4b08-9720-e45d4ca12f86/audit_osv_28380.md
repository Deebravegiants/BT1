# [M] UPX bele.h get_ne64 heap-based overflow

## Summary
Severity: Medium
Advisory: CVE-2024-3209
CVSS: 5.5 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-04-02
Source: https://osv.dev/vulnerability/CVE-2024-3209
Type: osv

## Details
A vulnerability was found in UPX up to 4.2.2. It has been rated as critical. This issue affects the function get_ne64 of the file bele.h. The manipulation leads to heap-based buffer overflow. The exploit has been disclosed to the public and may be used. The associated identifier of this vulnerability is VDB-259055. NOTE: The vendor was contacted early about this disclosure but did not respond in any way.

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/AE5OZ7YUEVLXVVS6PFP5RELVICQ4K6QK/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/J4DNK3AFPT4KIPTBKGCJ6FC3L7AWI2TN/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZHWZN2NX5W3WYA6ACJ746PAZXXNZETKD/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/3xxx/CVE-2024-3209.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-3209
- https://vuldb.com/?id.259055
- https://vuldb.com/?submit.304575
- https://vuldb.com/?ctiid.259055
- https://drive.google.com/drive/folders/1qlUXvycOzGJygfkdQB9dGO6VwNRRZoih?usp=sharing
