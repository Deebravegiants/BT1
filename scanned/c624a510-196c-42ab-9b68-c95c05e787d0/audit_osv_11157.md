# [M] CVE-2017-6420

## Summary
Severity: Medium
Advisory: CVE-2017-6420
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-07
Source: https://osv.dev/vulnerability/CVE-2017-6420
Type: osv

## Details
The wwunpack function in libclamav/wwunpack.c in ClamAV 0.99.2 allows remote attackers to cause a denial of service (use-after-free) via a crafted PE file with WWPack compression.

## References
- https://github.com/varsleak/varsleak-vul/blob/master/clamav-vul/use-after-free/clamav-use-after-free-pe.md
- https://security.gentoo.org/glsa/201804-16
- https://bugzilla.clamav.net/show_bug.cgi?id=11798
- https://github.com/vrtadmin/clamav-devel/commit/dfc00cd3301a42b571454b51a6102eecf58407bc
