# [M] CVE-2021-20321

## Summary
Severity: Medium
Advisory: CVE-2021-20321
Aliases: A-222644279, PUB-A-222644279
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-02-18
Source: https://osv.dev/vulnerability/CVE-2021-20321
Type: osv

## Details
A race condition accessing file object in the Linux kernel OverlayFS subsystem was found in the way users do rename in specific way with OverlayFS. A local user could use this flaw to crash the system.

## References
- https://lore.kernel.org/all/20211011134508.748956131%40linuxfoundation.org/
- https://lists.debian.org/debian-lts-announce/2022/03/msg00012.html
- https://www.debian.org/security/2022/dsa-5096
- https://bugzilla.redhat.com/show_bug.cgi?id=2013242
