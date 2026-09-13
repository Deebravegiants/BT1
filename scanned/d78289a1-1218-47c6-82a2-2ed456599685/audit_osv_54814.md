# [M] CVE-2024-45777

## Summary
Severity: Medium
Advisory: CVE-2024-45777
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-19
Source: https://osv.dev/vulnerability/CVE-2024-45777
Type: osv

## Details
A flaw was found in grub2. The calculation of the translation buffer when reading a language .mo file in grub_gettext_getstr_from_position() may overflow, leading to a Out-of-bound write. This issue can be leveraged by an attacker to overwrite grub2's sensitive heap data, eventually leading to the circumvention of secure boot protections.

## References
- https://access.redhat.com/errata/RHSA-2025:20532
- https://access.redhat.com/security/cve/CVE-2024-45777
- https://bugzilla.redhat.com/show_bug.cgi?id=2346343
