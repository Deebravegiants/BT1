# [H] CVE-2017-8854

## Summary
Severity: High
Advisory: CVE-2017-8854
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-05-09
Source: https://osv.dev/vulnerability/CVE-2017-8854
Type: osv

## Details
wolfSSL before 3.10.2 has an out-of-bounds memory access with loading crafted DH parameters, aka a buffer overflow triggered by a malformed temporary DH file.

## References
- https://github.com/wolfSSL/wolfssl/releases/tag/v3.10.2-stable
