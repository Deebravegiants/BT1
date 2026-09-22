# [H] BIT-artifactory-2021-3860

## Summary
Severity: High
Advisory: BIT-artifactory-2021-3860
Aliases: CVE-2021-3860
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-artifactory-2021-3860
Type: osv

## Affected
- Bitnami: `artifactory` — affected >=7.25.0 <7.25.4

## Details
JFrog Artifactory before 7.25.4 (Enterprise+ deployments only), is vulnerable to Blind SQL Injection by a low privileged authenticated user due to incomplete validation when performing an SQL query.

## References
- http://packetstormsecurity.com/files/177162/JFrog-Artifactory-SQL-Injection.html
- https://www.jfrog.com/confluence/display/JFROG/CVE-2021-3860%3A+Artifactory+Low+Privileged+Blind+SQL+Injection
- https://nvd.nist.gov/vuln/detail/CVE-2021-3860
