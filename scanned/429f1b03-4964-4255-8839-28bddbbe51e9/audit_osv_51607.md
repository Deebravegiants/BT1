# [H] CVE-2021-3506

## Summary
Severity: High
Advisory: CVE-2021-3506
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2021-04-19
Source: https://osv.dev/vulnerability/CVE-2021-3506
Type: osv

## Details
An out-of-bounds (OOB) memory access flaw was found in fs/f2fs/node.c in the f2fs module in the Linux kernel in versions before 5.12.0-rc4. A bounds check failure allows a local attacker to gain access to out-of-bounds memory leading to a system crash or a leak of internal kernel information. The highest threat from this vulnerability is to system availability.

## References
- https://www.mail-archive.com/linux-kernel%40vger.kernel.org/msg2520013.html
- https://lists.debian.org/debian-lts-announce/2021/06/msg00019.html
- https://security.netapp.com/advisory/ntap-20210611-0007/
- https://bugzilla.redhat.com/show_bug.cgi?id=1944298
- http://www.openwall.com/lists/oss-security/2021/05/08/1
- https://www.openwall.com/lists/oss-security/2021/03/28/2
