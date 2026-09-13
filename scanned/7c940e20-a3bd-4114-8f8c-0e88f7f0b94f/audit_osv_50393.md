# [M] CVE-2020-14390

## Summary
Severity: Medium
Advisory: CVE-2020-14390
CVSS: 5.6 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:L/I:L/A:H)
Published: 2020-09-18
Source: https://osv.dev/vulnerability/CVE-2020-14390
Type: osv

## Details
A flaw was found in the Linux kernel in versions before 5.9-rc6. When changing screen size, an out-of-bounds memory write can occur leading to memory corruption or a denial of service. Due to the nature of the flaw, privilege escalation cannot be fully ruled out.

## References
- https://lists.debian.org/debian-lts-announce/2020/10/msg00032.html
- https://lists.debian.org/debian-lts-announce/2020/10/msg00034.html
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00001.html
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00021.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1876788
