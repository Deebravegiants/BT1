# [M] CVE-2019-1010204

## Summary
Severity: Medium
Advisory: CVE-2019-1010204
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-07-23
Source: https://osv.dev/vulnerability/CVE-2019-1010204
Type: osv

## Details
GNU binutils gold gold v1.11-v1.16 (GNU binutils v2.21-v2.31.1) is affected by: Improper Input Validation, Signed/Unsigned Comparison, Out-of-bounds Read. The impact is: Denial of service. The component is: gold/fileread.cc:497, elfcpp/elfcpp_file.h:644. The attack vector is: An ELF file with an invalid e_shoff header field must be opened.

## References
- https://support.f5.com/csp/article/K05032915?utm_source=f5support&amp%3Butm_medium=RSS
- https://security.netapp.com/advisory/ntap-20190822-0001/
- https://sourceware.org/bugzilla/show_bug.cgi?id=23765
