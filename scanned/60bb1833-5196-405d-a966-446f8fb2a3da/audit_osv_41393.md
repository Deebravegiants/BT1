# [M] CVE-2026-59999

## Summary
Severity: Medium
Advisory: CVE-2026-59999
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/CVE-2026-59999
Type: osv

## Details
In sshd in OpenSSH before 10.4, DisableForwarding=yes was supposed to take precedence over PermitTunnel=yes, but did not.

## References
- https://marc.info/?l=openssh-unix-dev&m=178333966933090&w=2
- https://www.openssh.org/releasenotes.html#10.4p1
- https://www.openwall.com/lists/oss-security/2026/07/06/5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59999.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59999
