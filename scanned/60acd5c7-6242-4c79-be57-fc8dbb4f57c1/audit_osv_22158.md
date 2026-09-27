# [M] CVE-2022-23004

## Summary
Severity: Medium
Advisory: CVE-2022-23004
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2022-07-29
Source: https://osv.dev/vulnerability/CVE-2022-23004
Type: osv

## Details
When computing a shared secret or point multiplication on the NIST P-256 curve using a public key with an X coordinate of zero, an error is returned from the library, and an invalid unreduced value is written to the output buffer. This may be leveraged by an attacker to cause an error scenario, resulting in a limited denial of service for an individual user. The scope of impact cannot extend to other components.

## References
- https://www.westerndigital.com/support/product-security/wdc-22013-sweet-b-incorrect-output-vulnerabilities
