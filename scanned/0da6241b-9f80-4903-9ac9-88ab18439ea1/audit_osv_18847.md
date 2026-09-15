# [M] CVE-2020-36477

## Summary
Severity: Medium
Advisory: CVE-2020-36477
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2021-08-23
Source: https://osv.dev/vulnerability/CVE-2020-36477
Type: osv

## Details
An issue was discovered in Mbed TLS before 2.24.0. The verification of X.509 certificates when matching the expected common name (the cn argument of mbedtls_x509_crt_verify) with the actual certificate name is mishandled: when the subjecAltName extension is present, the expected name is compared to any name in that extension regardless of its type. This means that an attacker could impersonate a 4-byte or 16-byte domain by getting a certificate for the corresponding IPv4 or IPv6 address (this would require the attacker to control that IP address, though).

## References
- https://github.com/ARMmbed/mbedtls/issues/3498
- https://github.com/ARMmbed/mbedtls/releases/tag/v2.24.0
- https://security.gentoo.org/glsa/202301-08
