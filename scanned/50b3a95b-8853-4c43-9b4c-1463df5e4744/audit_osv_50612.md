# [M] CVE-2020-25656

## Summary
Severity: Medium
Advisory: CVE-2020-25656
Aliases: A-174904705, PUB-A-174904705
CVSS: 4.1 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-12-02
Source: https://osv.dev/vulnerability/CVE-2020-25656
Type: osv

## Details
A flaw was found in the Linux kernel. A use-after-free was found in the way the console subsystem was using ioctls KDGKBSENT and KDSKBSENT. A local user could use this flaw to get read memory access out of bounds. The highest threat from this vulnerability is to data confidentiality.

## References
- https://lists.debian.org/debian-lts-announce/2020/12/msg00015.html
- https://lists.debian.org/debian-lts-announce/2020/12/msg00027.html
- https://www.starwindsoftware.com/security/sw-20210325-0006/
- https://bugzilla.redhat.com/show_bug.cgi?id=1888726
- https://lkml.org/lkml/2020/10/29/528
- https://lkml.org/lkml/2020/10/16/84
