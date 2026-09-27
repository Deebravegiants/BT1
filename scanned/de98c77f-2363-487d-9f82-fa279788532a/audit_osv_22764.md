# [H] CVE-2022-38177

## Summary
Severity: High
Advisory: CVE-2022-38177
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-09-21
Source: https://osv.dev/vulnerability/CVE-2022-38177
Type: osv

## Details
By spoofing the target resolver with responses that have a malformed ECDSA signature, an attacker can trigger a small memory leak. It is possible to gradually erode available memory to the point where named crashes for lack of resources.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CV4GQWBPF7Y52J2FA24U6UMHQAOXZEF7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MRHB6J4Z7BKH4HPEKG5D35QGRD6ANNMT/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YZJQNUASODNVAWZV6STKG5SD6XIJ446S/
- https://lists.debian.org/debian-lts-announce/2022/10/msg00007.html
- https://security.gentoo.org/glsa/202210-25
- https://security.netapp.com/advisory/ntap-20221228-0010/
- https://www.debian.org/security/2022/dsa-5235
- http://www.openwall.com/lists/oss-security/2022/09/21/3
- https://kb.isc.org/docs/cve-2022-38177
