# [M] CVE-2021-38597

## Summary
Severity: Medium
Advisory: CVE-2021-38597
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-08-12
Source: https://osv.dev/vulnerability/CVE-2021-38597
Type: osv

## Details
wolfSSL before 4.8.1 incorrectly skips OCSP verification in certain situations of irrelevant response data that contains the NoCheck extension.

## References
- https://www.wolfssl.com/docs/wolfssl-changelog/
- https://github.com/wolfSSL/wolfssl/commit/f93083be72a3b3d956b52a7ec13f307a27b6e093
