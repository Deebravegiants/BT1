# [M] CVE-2018-14055

## Summary
Severity: Medium
Advisory: CVE-2018-14055
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-07-15
Source: https://osv.dev/vulnerability/CVE-2018-14055
Type: osv

## Details
ZNC before 1.7.1-rc1 does not properly validate untrusted lines coming from the network, allowing a non-admin user to escalate his privilege and inject rogue values into znc.conf.

## References
- https://security.gentoo.org/glsa/201807-03
- https://www.debian.org/security/2018/dsa-4252
- https://github.com/znc/znc/commit/a7bfbd93812950b7444841431e8e297e62cb524e
- https://github.com/znc/znc/commit/d22fef8620cdd87490754f607e7153979731c69d
