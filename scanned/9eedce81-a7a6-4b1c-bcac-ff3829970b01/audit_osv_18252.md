# [M] CVE-2020-25651

## Summary
Severity: Medium
Advisory: CVE-2020-25651
CVSS: 6.4 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:N/A:L)
Published: 2020-11-26
Source: https://osv.dev/vulnerability/CVE-2020-25651
Type: osv

## Details
A flaw was found in the SPICE file transfer protocol. File data from the host system can end up in full or in parts in the client connection of an illegitimate local user in the VM system. Active file transfers from other users could also be interrupted, resulting in a denial of service. The highest threat from this vulnerability is to data confidentiality as well as system availability. This flaw affects spice-vdagent versions 0.20 and prior.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GQT56LATVTB2DJOVVJOKQVMVUXYCT2VB/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OIWJ2EIQXWEA2VDBODEATHAT37X4CREP/
- https://lists.debian.org/debian-lts-announce/2021/01/msg00012.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1886359
- https://www.openwall.com/lists/oss-security/2020/11/04/1
