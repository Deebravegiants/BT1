# [M] MyBB: Email User CRLF injection

## Summary
Severity: Medium
Advisory: CVE-2026-45125
Aliases: GHSA-f626-53q9-pqm9
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-45125
Type: osv

## Details
MyBB is free and open source forum software. Prior to 1.8.40, the Email User controller does not sanitize sender names correctly, resulting in mail header injection. member.php?action=do_emailuser accepts the fromname HTTP parameter for guests or the stored username for authenticated users when the cansendemail group permission is enabled. When mail_handler is set to the default PHP mail value, the sender name is used without sanitization in Return-Path and Reply-To headers, allowing arbitrary headers to be injected with CRLF sequences. This issue is fixed in version 1.8.40.

## References
- https://github.com/mybb/mybb/releases/tag/mybb_1840
- https://mybb.com/versions/1.8.40
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45125.json
- https://github.com/mybb/mybb/security/advisories/GHSA-f626-53q9-pqm9
- https://nvd.nist.gov/vuln/detail/CVE-2026-45125
- https://github.com/mybb/mybb/commit/5046c56b515d4593297a4f65b0c6ccb0b55baa01
