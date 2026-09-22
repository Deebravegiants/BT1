# [M] CVE-2020-25652

## Summary
Severity: Medium
Advisory: CVE-2020-25652
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-11-26
Source: https://osv.dev/vulnerability/CVE-2020-25652
Type: osv

## Details
A flaw was found in the spice-vdagentd daemon, where it did not properly handle client connections that can be established via the UNIX domain socket in `/run/spice-vdagentd/spice-vdagent-sock`. Any unprivileged local guest user could use this flaw to prevent legitimate agents from connecting to the spice-vdagentd daemon, resulting in a denial of service. The highest threat from this vulnerability is to system availability. This flaw affects spice-vdagent versions 0.20 and prior.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GQT56LATVTB2DJOVVJOKQVMVUXYCT2VB/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OIWJ2EIQXWEA2VDBODEATHAT37X4CREP/
- https://lists.debian.org/debian-lts-announce/2021/01/msg00012.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1886366
- https://www.openwall.com/lists/oss-security/2020/11/04/1
