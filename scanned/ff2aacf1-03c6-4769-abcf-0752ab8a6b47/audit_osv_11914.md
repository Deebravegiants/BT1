# [M] CVE-2018-1000085

## Summary
Severity: Medium
Advisory: CVE-2018-1000085
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-03-13
Source: https://osv.dev/vulnerability/CVE-2018-1000085
Type: osv

## Details
ClamAV version version 0.99.3 contains a Out of bounds heap memory read vulnerability in XAR parser, function xar_hash_check() that can result in Leaking of memory, may help in developing exploit chains.. This attack appear to be exploitable via The victim must scan a crafted XAR file. This vulnerability appears to have been fixed in after commit d96a6b8bcc7439fa7e3876207aa0a8e79c8451b6.

## References
- https://lists.debian.org/debian-lts-announce/2018/03/msg00011.html
- https://security.gentoo.org/glsa/201804-16
- https://usn.ubuntu.com/3592-1/
- https://usn.ubuntu.com/3592-2/
- http://www.openwall.com/lists/oss-security/2017/09/29/4
- https://github.com/Cisco-Talos/clamav-devel/commit/d96a6b8bcc7439fa7e3876207aa0a8e79c8451b6
