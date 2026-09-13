# [M] CVE-2022-23001

## Summary
Severity: Medium
Advisory: CVE-2022-23001
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2022-07-29
Source: https://osv.dev/vulnerability/CVE-2022-23001
Type: osv

## Details
When compressing or decompressing elliptic curve points using the Sweet B library, an incorrect choice of sign bit is used. An attacker with user level privileges and no other user's assistance can exploit this vulnerability with only knowledge of the public key and the library. The resulting output may cause an error when used in other operations; for instance, verification of a valid signature under a decompressed public key may fail. This may be leveraged by an attacker to cause an error scenario in applications which use the library, resulting in a limited denial of service for an individual user. The scope of impact cannot extend to other components.

## References
- https://www.westerndigital.com/support/product-security/wdc-22013-sweet-b-incorrect-output-vulnerabilities
