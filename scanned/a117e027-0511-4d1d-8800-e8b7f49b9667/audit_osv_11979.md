# [H] CVE-2018-1000520

## Summary
Severity: High
Advisory: CVE-2018-1000520
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-06-26
Source: https://osv.dev/vulnerability/CVE-2018-1000520
Type: osv

## Details
ARM mbedTLS version 2.7.0 and earlier contains a Ciphersuite Allows Incorrectly Signed Certificates vulnerability in mbedtls_ssl_get_verify_result() that can result in ECDSA-signed certificates are accepted, when only RSA-signed ones should be.. This attack appear to be exploitable via Peers negotiate a TLS-ECDH-RSA-* ciphersuite. Any of the peers can then provide an ECDSA-signed certificate, when only an RSA-signed one should be accepted..

## References
- https://github.com/ARMmbed/mbedtls/issues/1561
