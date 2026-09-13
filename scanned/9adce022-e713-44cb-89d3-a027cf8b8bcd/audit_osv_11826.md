# [M] CVE-2017-9955

## Summary
Severity: Medium
Advisory: CVE-2017-9955
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-06-26
Source: https://osv.dev/vulnerability/CVE-2017-9955
Type: osv

## Details
The get_build_id function in opncls.c in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.28, allows remote attackers to cause a denial of service (heap-based buffer over-read and application crash) via a crafted file in which a certain size field is larger than a corresponding data field, as demonstrated by mishandling within the objdump program.

## References
- http://www.securityfocus.com/bid/99573
- https://sourceware.org/bugzilla/show_bug.cgi?id=21665
