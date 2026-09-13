# [H] Grub2: missing unregister call for gettext command may lead to use-after-free

## Summary
Severity: High
Advisory: CVE-2025-61662
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-11-18
Source: https://osv.dev/vulnerability/CVE-2025-61662
Type: osv

## Details
A Use-After-Free vulnerability has been discovered in GRUB's gettext module. This flaw stems from a programming error where the gettext command remains registered in memory after its module is unloaded. An attacker can exploit this condition by invoking the orphaned command, causing the application to access a memory location that is no longer valid. An attacker could exploit this vulnerability to cause grub to crash, leading to a Denial of Service. Possible data integrity or confidentiality compromise is not discarded.

## References
- http://www.openwall.com/lists/oss-security/2025/11/18/5
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.gnu.org/archive/html/grub-devel/2025-11/msg00155.html
- https://access.redhat.com/errata/RHSA-2026:10097
- https://access.redhat.com/errata/RHSA-2026:14773
- https://access.redhat.com/errata/RHSA-2026:15087
- https://access.redhat.com/errata/RHSA-2026:17596
- https://access.redhat.com/errata/RHSA-2026:4648
- https://access.redhat.com/errata/RHSA-2026:4649
- https://access.redhat.com/errata/RHSA-2026:4652
- https://access.redhat.com/errata/RHSA-2026:4653
- https://access.redhat.com/errata/RHSA-2026:4654
- https://access.redhat.com/errata/RHSA-2026:4760
- https://access.redhat.com/errata/RHSA-2026:4822
- https://access.redhat.com/errata/RHSA-2026:4823
- https://access.redhat.com/errata/RHSA-2026:4830
- https://access.redhat.com/errata/RHSA-2026:4900
- https://access.redhat.com/errata/RHSA-2026:4998
- https://access.redhat.com/errata/RHSA-2026:5074
- https://access.redhat.com/errata/RHSA-2026:5127
