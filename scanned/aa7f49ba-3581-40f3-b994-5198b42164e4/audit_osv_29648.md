# [H] Authenticated SQL Injection in i-Educar

## Summary
Severity: High
Advisory: CVE-2024-45059
Aliases: GHSA-2v4w-7xqr-hxmr
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-28
Source: https://osv.dev/vulnerability/CVE-2024-45059
Type: osv

## Details
i-Educar is free, fully online school management software that can be used by school secretaries, teachers, coordinators, and area managers. A SQL Injection vulnerability was found prior to the 2.9 branch in the `ieducar/intranet/funcionario_vinculo_det.php` file, which creates the query by concatenating the unsanitized GET parameter `cod_func`, allowing the attacker to obtain sensitive information such as emails and password hashes. Commit 7824b95745fa2da6476b9901041d9c854bf52ffe fixes the issue.

## References
- https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html
- https://portswigger.net/web-security/sql-injection
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45059.json
- https://github.com/portabilis/i-educar/security/advisories/GHSA-2v4w-7xqr-hxmr
- https://nvd.nist.gov/vuln/detail/CVE-2024-45059
- https://github.com/portabilis/i-educar/commit/7824b95745fa2da6476b9901041d9c854bf52ffe
