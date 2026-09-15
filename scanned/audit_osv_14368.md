# [H] CVE-2018-9860

## Summary
Severity: High
Advisory: CVE-2018-9860
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-04-12
Source: https://osv.dev/vulnerability/CVE-2018-9860
Type: osv

## Details
An issue was discovered in Botan 1.11.32 through 2.x before 2.6.0. An off-by-one error when processing malformed TLS-CBC ciphertext could cause the receiving side to include in the HMAC computation exactly 64K bytes of data following the record buffer, aka an over-read. The MAC comparison will subsequently fail and the connection will be closed. This could be used for denial of service. No information leak occurs.

## References
- https://botan.randombit.net/security.html
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=7434
