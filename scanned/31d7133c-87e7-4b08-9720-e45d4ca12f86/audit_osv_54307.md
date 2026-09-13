# [M] CVE-2023-4732

## Summary
Severity: Medium
Advisory: CVE-2023-4732
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-10-03
Source: https://osv.dev/vulnerability/CVE-2023-4732
Type: osv

## Details
A flaw was found in pfn_swap_entry_to_page in memory management subsystem in the Linux Kernel. In this flaw, an attacker with a local user privilege may cause a denial of service problem due to a BUG statement referencing pmd_t x.

## References
- https://access.redhat.com/security/cve/CVE-2023-4732
- https://access.redhat.com/errata/RHSA-2023:6901
- https://access.redhat.com/errata/RHSA-2023:7077
- https://access.redhat.com/errata/RHSA-2023:7539
- https://access.redhat.com/errata/RHSA-2024:0412
- https://bugzilla.redhat.com/show_bug.cgi?id=2236982
