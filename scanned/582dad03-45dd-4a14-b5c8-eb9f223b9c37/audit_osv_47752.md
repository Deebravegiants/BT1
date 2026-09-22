# [H] CVE-2017-11473

## Summary
Severity: High
Advisory: CVE-2017-11473
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-07-20
Source: https://osv.dev/vulnerability/CVE-2017-11473
Type: osv

## Details
Buffer overflow in the mp_override_legacy_irq() function in arch/x86/kernel/acpi/boot.c in the Linux kernel through 3.2 allows local users to gain privileges via a crafted ACPI table.

## References
- https://usn.ubuntu.com/3754-1/
- http://www.securityfocus.com/bid/100010
- https://access.redhat.com/errata/RHSA-2018:0654
- https://git.kernel.org/pub/scm/linux/kernel/git/tip/tip.git/commit/?id=96301209473afd3f2f274b91cb7082d161b9be65
- https://source.android.com/security/bulletin/pixel/2018-01-01
- https://git.kernel.org/pub/scm/linux/kernel/git/tip/tip.git/commit/?id=70ac67826602edf8c0ccb413e5ba7eacf597a60c
- https://git.kernel.org/pub/scm/linux/kernel/git/tip/tip.git/commit/?id=dad5ab0db8deac535d03e3fe3d8f2892173fa6a4
