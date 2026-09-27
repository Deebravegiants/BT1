# [H] CVE-2018-20954

## Summary
Severity: High
Advisory: CVE-2018-20954
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-08-08
Source: https://osv.dev/vulnerability/CVE-2018-20954
Type: osv

## Details
The "Security and Privacy" Encryption feature in Mailpile before 1.0.0rc4 does not exclude disabled, revoked, and expired keys.

## References
- https://github.com/mailpile/Mailpile/compare/1.0.0rc3...1.0.0rc4
- https://github.com/mailpile/Mailpile/pull/2145
- https://github.com/mailpile/Mailpile/commit/49b64f62ade9ade3dff9337c7bbc1171eab3d59e
