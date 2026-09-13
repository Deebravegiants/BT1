# [H] CVE-2021-45450

## Summary
Severity: High
Advisory: CVE-2021-45450
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-12-21
Source: https://osv.dev/vulnerability/CVE-2021-45450
Type: osv

## Details
In Mbed TLS before 2.28.0 and 3.x before 3.1.0, psa_cipher_generate_iv and psa_cipher_encrypt allow policy bypass or oracle-based decryption when the output buffer is at memory locations accessible to an untrusted application.

## References
- https://github.com/ARMmbed/mbedtls/releases/tag/v2.28.0
- https://github.com/ARMmbed/mbedtls/releases/tag/v3.1.0
- https://security.gentoo.org/glsa/202301-08
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IL66WKJGXY5AXMTFE7QDMGL3RIBD6PX5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TALJHOYAYSUJTLN6BYGLO4YJGNZUY74W/
