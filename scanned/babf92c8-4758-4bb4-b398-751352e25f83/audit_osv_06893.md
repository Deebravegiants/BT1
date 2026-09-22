# [H] Pre-authentication Denial of Service Stack Overflow Vulnerability in JSON Parsing via Excessive Recursion in MongoDB

## Summary
Severity: High
Advisory: BIT-mongodb-2025-6710
Aliases: CVE-2025-6710
Ecosystem: Bitnami
Published: 2025-09-16
Source: https://osv.dev/vulnerability/BIT-mongodb-2025-6710
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.0.0 <8.0.5

## Details
MongoDB Server may be susceptible to stack overflow due to JSON parsing mechanism, where specifically crafted JSON inputs may induce unwarranted levels of recursion, resulting in excessive stack space consumption. Such inputs can lead to a stack overflow that causes the server to crash which could occur pre-authorisation. This issue affects MongoDB Server v7.0 versions prior to 7.0.17 and MongoDB Server v8.0 versions prior to 8.0.5.

The same issue affects MongoDB Server v6.0 versions prior to 6.0.21, but an attacker can only induce denial of service after authenticating.

## References
- https://jira.mongodb.org/browse/SERVER-106749
- https://nvd.nist.gov/vuln/detail/CVE-2025-6710
