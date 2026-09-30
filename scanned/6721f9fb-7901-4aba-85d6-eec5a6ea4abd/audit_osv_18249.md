# [H] CVE-2020-25643

## Summary
Severity: High
Advisory: CVE-2020-25643
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-10-06
Source: https://osv.dev/vulnerability/CVE-2020-25643
Type: osv

## Details
A flaw was found in the HDLC_PPP module of the Linux kernel in versions before 5.9-rc7. Memory corruption and a read overflow is caused by improper input validation in the ppp_cp_parse_cr function which can cause the system to crash or cause a denial of service. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00021.html
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00042.html
- https://lists.debian.org/debian-lts-announce/2020/10/msg00034.html
- https://security.netapp.com/advisory/ntap-20201103-0002/
- https://www.debian.org/security/2020/dsa-4774
- https://lists.debian.org/debian-lts-announce/2020/10/msg00028.html
- https://lists.debian.org/debian-lts-announce/2020/10/msg00032.html
- https://www.starwindsoftware.com/security/sw-20210325-0002/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=66d42ed8b25b64eb63111a2b8582c5afc8bf1105
- https://bugzilla.redhat.com/show_bug.cgi?id=1879981
