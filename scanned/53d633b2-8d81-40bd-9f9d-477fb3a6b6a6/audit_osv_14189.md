# [H] CVE-2018-7738

## Summary
Severity: High
Advisory: CVE-2018-7738
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-03-07
Source: https://osv.dev/vulnerability/CVE-2018-7738
Type: osv

## Details
In util-linux before 2.32-rc1, bash-completion/umount allows local users to gain privileges by embedding shell commands in a mountpoint name, which is mishandled during a umount command (within Bash) by a different user, as demonstrated by logging in as root and entering umount followed by a tab character for autocompletion.

## References
- https://usn.ubuntu.com/4512-1/
- http://www.securityfocus.com/bid/103367
- https://security.netapp.com/advisory/ntap-20241213-0002/
- https://www.debian.org/security/2018/dsa-4134
- https://github.com/karelzak/util-linux/issues/539
- https://bugs.debian.org/892179
- https://github.com/karelzak/util-linux/commit/75f03badd7ed9f1dd951863d75e756883d3acc55
