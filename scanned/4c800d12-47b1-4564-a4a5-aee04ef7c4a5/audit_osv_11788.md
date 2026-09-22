# [H] CVE-2017-9752

## Summary
Severity: High
Advisory: CVE-2017-9752
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-06-19
Source: https://osv.dev/vulnerability/CVE-2017-9752
Type: osv

## Details
bfd/vms-alpha.c in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.28, allows remote attackers to cause a denial of service (buffer overflow and application crash) or possibly have unspecified other impact via a crafted binary file, as demonstrated by mishandling of this file in the _bfd_vms_get_value and _bfd_vms_slurp_etir functions during "objdump -D" execution.

## References
- http://www.securityfocus.com/bid/99122
- https://sourceware.org/bugzilla/show_bug.cgi?id=21589
