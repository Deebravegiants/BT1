# [H] Kernel: ktls overwrites readonly memory pages when using function splice with a ktls socket as destination

## Summary
Severity: High
Advisory: CVE-2024-0646
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-01-17
Source: https://osv.dev/vulnerability/CVE-2024-0646
Type: osv

## Details
An out-of-bounds memory write flaw was found in the Linux kernel’s Transport Layer Security functionality in how a user calls a function splice with a ktls socket as the destination. This flaw allows a local user to crash or potentially escalate their privileges on the system.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://git.kernel.org/pub/scm/linux/kernel
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=c5a595000e267
- https://lists.debian.org/debian-lts-announce/2024/06/msg00016.html
- https://access.redhat.com/errata/RHSA-2024:0723
- https://access.redhat.com/errata/RHSA-2024:0724
- https://access.redhat.com/errata/RHSA-2024:0725
- https://access.redhat.com/errata/RHSA-2024:0850
- https://access.redhat.com/errata/RHSA-2024:0851
- https://access.redhat.com/errata/RHSA-2024:0876
- https://access.redhat.com/errata/RHSA-2024:0881
- https://access.redhat.com/errata/RHSA-2024:0897
- https://access.redhat.com/errata/RHSA-2024:1248
- https://access.redhat.com/errata/RHSA-2024:1250
- https://access.redhat.com/errata/RHSA-2024:1251
- https://access.redhat.com/errata/RHSA-2024:1253
- https://access.redhat.com/errata/RHSA-2024:1268
- https://access.redhat.com/errata/RHSA-2024:1269
- https://access.redhat.com/errata/RHSA-2024:1278
