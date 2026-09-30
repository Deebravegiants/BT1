# [H] bcachefs: Fix sb_field_downgrade validation

## Summary
Severity: High
Advisory: CVE-2024-41086
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-07-29
Source: https://osv.dev/vulnerability/CVE-2024-41086
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.9.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

bcachefs: Fix sb_field_downgrade validation

- bch2_sb_downgrade_validate() wasn't checking for a downgrade entry
  extending past the end of the superblock section

- for_each_downgrade_entry() is used in to_text() and needs to work on
  malformed input; it also was missing a check for a field extending
  past the end of the section

## References
- https://git.kernel.org/stable/c/692aa7a54b2b28d59f24b3bf8250837805484b99
- https://git.kernel.org/stable/c/bf920ed92ef24dcd6970c88881cd4700b3acf05b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41086.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41086
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
