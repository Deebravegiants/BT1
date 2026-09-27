# [H] CVE-2017-9748

## Summary
Severity: High
Advisory: CVE-2017-9748
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-06-19
Source: https://osv.dev/vulnerability/CVE-2017-9748
Type: osv

## Details
The ieee_object_p function in bfd/ieee.c in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.28, might allow remote attackers to cause a denial of service (buffer overflow and application crash) or possibly have unspecified other impact via a crafted binary file, as demonstrated by mishandling of this file during "objdump -D" execution. NOTE: this may be related to a compiler bug.

## References
- https://www.exploit-db.com/exploits/42202/
- http://www.securityfocus.com/bid/99110
- https://sourceware.org/bugzilla/show_bug.cgi?id=21582
