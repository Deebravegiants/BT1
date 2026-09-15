# [M] CVE-2026-59995

## Summary
Severity: Medium
Advisory: CVE-2026-59995
CVSS: 4.2 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:L/A:L)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/CVE-2026-59995
Type: osv

## Details
sftp in OpenSSH before 10.4 does not properly constrain the location of downloaded files when "sftp server:/path ." is used with an attacker-controlled server.

## References
- https://marc.info/?l=openssh-unix-dev&m=178333966933090&w=2
- https://www.openssh.org/releasenotes.html#10.4p1
- https://www.openwall.com/lists/oss-security/2026/07/06/5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59995.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59995
