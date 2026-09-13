# [H] CVE-2020-15309

## Summary
Severity: High
Advisory: CVE-2020-15309
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-08-21
Source: https://osv.dev/vulnerability/CVE-2020-15309
Type: osv

## Details
An issue was discovered in wolfSSL before 4.5.0, when single precision is not employed. Local attackers can conduct a cache-timing attack against public key operations. These attackers may already have obtained sensitive information if the affected system has been used for private key operations (e.g., signing with a private key).

## References
- https://github.com/wolfSSL/wolfssl/releases/tag/v4.5.0-stable
- https://arxiv.org/abs/2008.12188
