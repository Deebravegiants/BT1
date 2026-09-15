# [H] CVE-2017-6492

## Summary
Severity: High
Advisory: CVE-2017-6492
CVSS: 7.2 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-03-05
Source: https://osv.dev/vulnerability/CVE-2017-6492
Type: osv

## Details
SQL Injection was discovered in adm_program/modules/dates/dates_function.php in Admidio 3.2.5. The POST parameter dat_cat_id is concatenated into a SQL query without any input validation/sanitization.

## References
- http://www.securityfocus.com/bid/97034
- https://github.com/hamkovic/Admidio-3.2.5-SQLi
