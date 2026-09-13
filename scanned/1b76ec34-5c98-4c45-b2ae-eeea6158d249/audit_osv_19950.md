# [H] CVE-2021-28242

## Summary
Severity: High
Advisory: CVE-2021-28242
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-04-15
Source: https://osv.dev/vulnerability/CVE-2021-28242
Type: osv

## Details
SQL Injection in the "evoadm.php" component of b2evolution v7.2.2-stable allows remote attackers to obtain sensitive database information by injecting SQL commands into the "cf_name" parameter when creating a new filter under the "Collections" tab.

## References
- https://github.com/b2evolution/b2evolution/issues/109
- https://deadsh0t.medium.com/authenticated-boolean-based-blind-error-based-sql-injection-b752225f0644
- http://packetstormsecurity.com/files/162489/b2evolution-7-2-2-SQL-Injection.html
