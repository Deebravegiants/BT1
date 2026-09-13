# [M] CVE-2016-2858

## Summary
Severity: Medium
Advisory: CVE-2016-2858
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2016-04-07
Source: https://osv.dev/vulnerability/CVE-2016-2858
Type: osv

## Details
QEMU, when built with the Pseudo Random Number Generator (PRNG) back-end support, allows local guest OS users to cause a denial of service (process crash) via an entropy request, which triggers arbitrary stack based allocation and memory corruption.

## References
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=60253ed1e6ec6d8e5ef2efe7bf755f475dce9956
- http://www.openwall.com/lists/oss-security/2016/03/04/1
- http://www.openwall.com/lists/oss-security/2016/03/07/4
- http://www.securityfocus.com/bid/84134
- http://www.ubuntu.com/usn/USN-2974-1
- https://lists.debian.org/debian-lts-announce/2018/11/msg00038.html
- https://security.gentoo.org/glsa/201604-01
- https://bugzilla.redhat.com/show_bug.cgi?id=1314676
