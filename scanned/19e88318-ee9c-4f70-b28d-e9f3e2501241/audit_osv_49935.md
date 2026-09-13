# [H] CVE-2019-5008

## Summary
Severity: High
Advisory: CVE-2019-5008
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-04-19
Source: https://osv.dev/vulnerability/CVE-2019-5008
Type: osv

## Details
hw/sparc64/sun4u.c in QEMU 3.1.50 is vulnerable to a NULL pointer dereference, which allows the attacker to cause a denial of service via a device driver.

## References
- https://git.qemu.org/?p=qemu.git%3Ba=history%3Bf=hw/sparc64/sun4u.c%3Bhb=HEAD
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BOE3PVFPMWMXV3DGP2R3XIHAF2ZQU3FS/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RVDHJB2QKXNDU7OFXIHIL5O5VN5QCSZL/
- https://usn.ubuntu.com/3978-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00000.html
- http://www.securityfocus.com/bid/108024
- https://fakhrizulkifli.github.io/posts/2019/01/03/CVE-2019-5008/
