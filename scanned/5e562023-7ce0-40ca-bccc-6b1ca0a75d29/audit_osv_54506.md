# [M] CVE-2024-0340

## Summary
Severity: Medium
Advisory: CVE-2024-0340
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-01-09
Source: https://osv.dev/vulnerability/CVE-2024-0340
Type: osv

## Details
A vulnerability was found in vhost_new_msg in drivers/vhost/vhost.c in the Linux kernel, which does not properly initialize memory in messages passed between virtual guests and the host operating system in the vhost/vhost.c:vhost_new_msg() function. This issue can allow local privileged users to read some kernel memory contents when reading from the /dev/vhost-net device file.

## References
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://access.redhat.com/errata/RHSA-2024:3618
- https://access.redhat.com/errata/RHSA-2024:3627
- https://access.redhat.com/errata/RHSA-2024:9315
- https://access.redhat.com/errata/RHSA-2025:7526
- https://access.redhat.com/security/cve/CVE-2024-0340
- https://bugzilla.redhat.com/show_bug.cgi?id=2257406
- https://lore.kernel.org/lkml/5kn47peabxjrptkqa6dwtyus35ahf4pcj4qm4pumse33kxqpjw@mec4se5relrc/T/
