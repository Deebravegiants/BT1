# [H] sshd in OpenSSH before 10.4 allows remote attackers to cause a denial of service (resource...

## Summary
Severity: High
Advisory: JLSEC-2026-1324
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-14
Source: https://osv.dev/vulnerability/JLSEC-2026-1324
Type: osv

## Affected
- Julia: `OpenSSH_jll` — affected >=0 <10.4.1+0

## Details
sshd in OpenSSH before 10.4 allows remote attackers to cause a denial of service (resource consumption from excessive authentication attempts) because MaxAuthTries was mishandled for GSSAPIAuthentication.

## References
- https://github.com/advisories/GHSA-76jm-35gr-hwcm
- https://marc.info/?l=openssh-unix-dev&m=178333966933090&w=2
- https://nvd.nist.gov/vuln/detail/CVE-2026-60000
- https://www.openssh.org/releasenotes.html#10.4p1
- https://www.openwall.com/lists/oss-security/2026/07/06/5
