# [M] CVE-2020-25653

## Summary
Severity: Medium
Advisory: CVE-2020-25653
CVSS: 6.3 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2020-11-26
Source: https://osv.dev/vulnerability/CVE-2020-25653
Type: osv

## Details
A race condition vulnerability was found in the way the spice-vdagentd daemon handled new client connections. This flaw may allow an unprivileged local guest user to become the active agent for spice-vdagentd, possibly resulting in a denial of service or information leakage from the host. The highest threat from this vulnerability is to data confidentiality as well as system availability. This flaw affects spice-vdagent versions 0.20 and prior.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GQT56LATVTB2DJOVVJOKQVMVUXYCT2VB/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OIWJ2EIQXWEA2VDBODEATHAT37X4CREP/
- https://lists.debian.org/debian-lts-announce/2021/01/msg00012.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1886372
- https://www.openwall.com/lists/oss-security/2020/11/04/1
