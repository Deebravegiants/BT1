# [H] CVE-2017-5207

## Summary
Severity: High
Advisory: CVE-2017-5207
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-03-23
Source: https://osv.dev/vulnerability/CVE-2017-5207
Type: osv

## Details
Firejail before 0.9.44.4, when running a bandwidth command, allows local users to gain root privileges via the --shell argument.

## References
- http://www.securityfocus.com/bid/97385
- https://firejail.wordpress.com/download-2/release-notes/
- http://www.openwall.com/lists/oss-security/2017/01/07/6
- https://github.com/netblue30/firejail/commit/5d43fdcd215203868d440ffc42036f5f5ffc89fc
- https://github.com/netblue30/firejail/issues/1023
- https://security.gentoo.org/glsa/201701-62
