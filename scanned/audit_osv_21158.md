# [M] CVE-2021-40943

## Summary
Severity: Medium
Advisory: CVE-2021-40943
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-06-28
Source: https://osv.dev/vulnerability/CVE-2021-40943
Type: osv

## Details
In Bento4 1.6.0-638, there is a null pointer reference in the function AP4_DescriptorListInspector::Action function in Ap4Descriptor.h:124 , as demonstrated by GPAC. This can cause a denial of service (DOS).

## References
- https://github.com/axiomatic-systems/Bento4/issues/643
