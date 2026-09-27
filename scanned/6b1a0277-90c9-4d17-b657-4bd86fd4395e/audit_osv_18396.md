# [H] CVE-2020-27207

## Summary
Severity: High
Advisory: CVE-2020-27207
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-11-26
Source: https://osv.dev/vulnerability/CVE-2020-27207
Type: osv

## Details
Zetetic SQLCipher 4.x before 4.4.1 has a use-after-free, related to sqlcipher_codec_pragma and sqlite3Strlen30 in sqlite3.c. A remote denial of service attack can be performed. For example, a SQL injection can be used to execute the crafted SQL command sequence. After that, some unexpected RAM data is read.

## References
- https://github.com/sqlcipher/sqlcipher/compare/v4.4.0...v4.4.1
- https://www.telekom.com/en/corporate-responsibility/data-protection-data-security/security/details/advisories-504842
- https://www.telekom.com/resource/blob/612796/9f221708832a465f03585a45d7f59b45/dl-201112-denial-of-serviceen-data.pdf
