# [H] CVE-2021-3549

## Summary
Severity: High
Advisory: CVE-2021-3549
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H)
Published: 2021-05-26
Source: https://osv.dev/vulnerability/CVE-2021-3549
Type: osv

## Details
An out of bounds flaw was found in GNU binutils objdump utility version 2.36. An attacker could use this flaw and pass a large section to avr_elf32_load_records_from_section() probably resulting in a crash or in some cases memory corruption. The highest threat from this vulnerability is to integrity as well as system availability.

## References
- https://security.gentoo.org/glsa/202208-30
- https://security.netapp.com/advisory/ntap-20250228-0005/
- https://bugzilla.redhat.com/show_bug.cgi?id=1960717
