# [H] JLSEC-2026-453

## Summary
Severity: High
Advisory: JLSEC-2026-453
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-05
Source: https://osv.dev/vulnerability/JLSEC-2026-453
Type: osv

## Affected
- Julia: `Ncurses_jll` — affected >=0 <6.4.0+0

## Details
ncurses before 6.4 20230408, when used by a setuid application, allows local users to trigger security-relevant memory corruption via malformed data in a terminfo database file that is found in `$HOME/.terminfo` or reached via the TERMINFO or TERM environment variable.

## References
- http://ncurses.scripts.mit.edu/?p=ncurses.git%3Ba=commit%3Bh=eb51b1ea1f75a0ec17c9c5937cb28df1e8eeec56
- http://www.openwall.com/lists/oss-security/2023/04/19/10
- http://www.openwall.com/lists/oss-security/2023/04/19/11
- https://lists.debian.org/debian-lts-announce/2023/12/msg00004.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LU4MYMKFEZQ5VSCVLRIZGDQOUW3T44GT/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LU4MYMKFEZQ5VSCVLRIZGDQOUW3T44GT/
- https://security.netapp.com/advisory/ntap-20230517-0009/
- https://support.apple.com/kb/HT213843
- https://support.apple.com/kb/HT213844
- https://support.apple.com/kb/HT213845
- https://www.openwall.com/lists/oss-security/2023/04/12/5
- https://www.openwall.com/lists/oss-security/2023/04/13/4
