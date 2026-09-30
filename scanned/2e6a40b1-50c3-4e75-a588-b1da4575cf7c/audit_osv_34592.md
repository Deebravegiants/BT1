# [M] Arbitrary file read by system admin via path traversal

## Summary
Severity: Medium
Advisory: CVE-2025-6233
Aliases: GHSA-wvw2-3jh4-4c39, GO-2025-3820
CVSS: 6.8 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:N/A:N)
Published: 2025-07-18
Source: https://osv.dev/vulnerability/CVE-2025-6233
Type: osv

## Details
Mattermost versions 10.8.x <= 10.8.1, 10.7.x <= 10.7.3, 10.5.x <= 10.5.7, 9.11.x <= 9.11.16 fail to sanitize input paths of file attachments in the bulk import JSONL file, which allows a system admin to read arbitrary system files via path traversal.

## References
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/6xxx/CVE-2025-6233.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-6233
