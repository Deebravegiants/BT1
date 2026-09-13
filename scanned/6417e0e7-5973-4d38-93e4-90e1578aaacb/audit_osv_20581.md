# [M] CVE-2021-35307

## Summary
Severity: Medium
Advisory: CVE-2021-35307
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-08-05
Source: https://osv.dev/vulnerability/CVE-2021-35307
Type: osv

## Details
An issue was discovered in Bento4 through v1.6.0-636. A NULL pointer dereference exists in the AP4_DescriptorFinder::Test component located in /Core/Ap4Descriptor.h. It allows an attacker to cause a denial of service (DOS).

## References
- https://github.com/axiomatic-systems/Bento4/issues/616
