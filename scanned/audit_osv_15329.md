# [C] CVE-2019-15562

## Summary
Severity: Critical
Advisory: CVE-2019-15562
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-08-26
Source: https://osv.dev/vulnerability/CVE-2019-15562
Type: osv

## Details
GORM before 1.9.10 allows SQL injection via incomplete parentheses. NOTE: Misusing Gorm by passing untrusted user input where Gorm expects trusted SQL fragments is a vulnerability in the application, not in Gorm

## References
- https://github.com/go-gorm/gorm/issues/2517#issuecomment-638145427
- https://github.com/go-gorm/gorm/pull/2519
- https://github.com/go-gorm/gorm/pull/2674
- https://github.com/jinzhu/gorm/releases/tag/v1.9.10
