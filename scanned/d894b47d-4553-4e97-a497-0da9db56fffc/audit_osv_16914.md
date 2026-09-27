# [M] CVE-2020-10702

## Summary
Severity: Medium
Advisory: CVE-2020-10702
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-06-04
Source: https://osv.dev/vulnerability/CVE-2020-10702
Type: osv

## Details
A flaw was found in QEMU in the implementation of the Pointer Authentication (PAuth) support for ARM introduced in version 4.0 and fixed in version 5.0.0. A general failure of the signature generation process caused every PAuth-enforced pointer to be signed with the same signature. A local attacker could obtain the signature of a protected pointer and abuse this flaw to bypass PAuth protection for all programs running on QEMU.

## References
- https://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=de0b1bae6461f67243282555475f88b2384a1eb9
- https://security.netapp.com/advisory/ntap-20200724-0007/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-10702
