# [H] SQL Injection in thinkjs

## Summary
Severity: High
Advisory: GHSA-q5mq-6fjg-4mw8
CVE: CVE-2020-21176
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-11-19
Source: https://github.com/advisories/GHSA-q5mq-6fjg-4mw8
Type: github-advisory

## Affected
- npm: `thinkjs` — affected >=0

## Details
SQL injection vulnerability in the model.increment and model.decrement function in ThinkJS 3.2.10 allows remote attackers to execute arbitrary SQL commands via the step parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-21176
- https://blog.jiguang.xyz/posts/thinkjs-sql-injection
- https://github.com/thinkjs/thinkjs
