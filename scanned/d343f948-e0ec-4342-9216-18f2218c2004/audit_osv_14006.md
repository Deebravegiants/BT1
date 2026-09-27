# [H] CVE-2018-6343

## Summary
Severity: High
Advisory: CVE-2018-6343
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-12-31
Source: https://osv.dev/vulnerability/CVE-2018-6343
Type: osv

## Details
Proxygen fails to validate that a secondary auth manager is set before dereferencing it. That can cause a denial of service issue when parsing a Certificate/CertificateRequest HTTP2 Frame over a fizz (TLS 1.3) transport. This issue affects Proxygen releases starting from v2018.10.29.00 until the fix in v2018.11.19.00.

## References
- https://github.com/facebook/proxygen/commit/0600ebe59c3e82cd012def77ca9ca1918da74a71
