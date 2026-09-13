# [M] CVE-2022-23003

## Summary
Severity: Medium
Advisory: CVE-2022-23003
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2022-07-29
Source: https://osv.dev/vulnerability/CVE-2022-23003
Type: osv

## Details
When computing a shared secret or point multiplication on the NIST P-256 curve that results in an X coordinate of zero, the resulting output is not properly reduced modulo the P-256 field prime and is invalid. The resulting output may cause an error when used in other operations. This may be leveraged by an attacker to cause an error scenario or incorrect choice of session key in applications which use the library, resulting in a limited denial of service for an individual user. The scope of impact cannot extend to other components.

## References
- https://www.westerndigital.com/support/product-security/wdc-22013-sweet-b-incorrect-output-vulnerabilities
