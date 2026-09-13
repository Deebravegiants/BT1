# [M] Misskey: JSON-LD signature validation + compaction may lead to improper activity handling

## Summary
Severity: Medium
Advisory: CVE-2026-46713
Aliases: GHSA-w8x2-gpq6-jxvf
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:H/VA:N/SC:N/SI:H/SA:N)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-46713
Type: osv

## Details
Misskey is an open source, federated social media platform. Versions 12.37.0 and later, but prior to 2026.5.4, contain a vulnerability in the JSON-LD signature validation and compaction process that allows spoofed activities to be accepted as valid. This issue has been fixed in version 2026.5.4.

## References
- https://github.com/misskey-dev/misskey/releases/tag/2026.5.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46713.json
- https://github.com/misskey-dev/misskey/security/advisories/GHSA-w8x2-gpq6-jxvf
- https://nvd.nist.gov/vuln/detail/CVE-2026-46713
