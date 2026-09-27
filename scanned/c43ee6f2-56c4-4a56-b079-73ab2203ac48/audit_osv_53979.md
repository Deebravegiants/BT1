# [H] CVE-2023-3567

## Summary
Severity: High
Advisory: CVE-2023-3567
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2023-07-24
Source: https://osv.dev/vulnerability/CVE-2023-3567
Type: osv

## Details
A use-after-free flaw was found in vcs_read in drivers/tty/vt/vc_screen.c in vc_screen in the Linux Kernel. This issue may allow an attacker with local user access to cause a system crash or leak internal kernel information.

## References
- http://packetstormsecurity.com/files/175963/Kernel-Live-Patch-Security-Notice-LSN-0099-1.html
- http://packetstormsecurity.com/files/175072/Kernel-Live-Patch-Security-Notice-LSN-0098-1.html
- https://access.redhat.com/errata/RHSA-2024:0432
- https://access.redhat.com/errata/RHSA-2024:0439
- https://access.redhat.com/errata/RHSA-2024:0448
- https://access.redhat.com/errata/RHSA-2024:0575
- https://access.redhat.com/errata/RHSA-2024:2394
- https://access.redhat.com/errata/RHSA-2024:3138
- https://access.redhat.com/errata/RHSA-2024:0412
- https://access.redhat.com/errata/RHSA-2024:0431
- https://access.redhat.com/errata/RHSA-2024:2950
- https://access.redhat.com/security/cve/CVE-2023-3567
- https://bugzilla.redhat.com/show_bug.cgi?id=2221463
- https://www.spinics.net/lists/stable-commits/msg285184.html
