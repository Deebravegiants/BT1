# [M] CVE-2018-14056

## Summary
Severity: Medium
Advisory: CVE-2018-14056
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2018-07-15
Source: https://osv.dev/vulnerability/CVE-2018-14056
Type: osv

## Details
ZNC before 1.7.1-rc1 is prone to a path traversal flaw via ../ in a web skin name to access files outside of the intended skins directories.

## References
- https://security.gentoo.org/glsa/201807-03
- https://www.debian.org/security/2018/dsa-4252
- https://github.com/znc/znc/commit/a4a5aeeb17d32937d8c7d743dae9a4cc755ce773
