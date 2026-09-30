# [M] NanaZip UFS Archive Parser Memory Corruption via Unvalidated Directory Record Length

## Summary
Severity: Medium
Advisory: CVE-2026-27711
Aliases: GHSA-rjwv-4w7x-hc9c
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-02-25
Source: https://osv.dev/vulnerability/CVE-2026-27711
Type: osv

## Details
NanaZip is an open source file archive. Starting in version 5.0.1252.0 and prior to versions 6.0.1638.0 and 6.5.1638.0, a memory corruption vulnerability in NanaZip’s UFS parser allows a crafted `.ufs/.ufs2/.img` file to trigger out-of-bounds memory access during archive open/listing. The bug is reachable via normal user file-open flow and can cause process crash, hang, and potentially exploitable heap corruption. Versions 6.0.1638.0 and 6.5.1638.0 fix the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27711.json
- https://github.com/M2Team/NanaZip/security/advisories/GHSA-rjwv-4w7x-hc9c
- https://nvd.nist.gov/vuln/detail/CVE-2026-27711
