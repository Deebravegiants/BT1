# [H] Denial of Service when processing malformed Role names

## Summary
Severity: High
Advisory: BIT-mongodb-2020-7925
Aliases: CVE-2020-7925
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mongodb-2020-7925
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=4.2.0 <4.2.9

## Details
Incorrect validation of user input in the role name parser may lead to use of uninitialized memory allowing an unauthenticated attacker to use a specially crafted request to cause a denial of service. This issue affects MongoDB Server v4.4 versions prior to 4.4.0; MongoDB Server v4.2 versions prior to 4.2.9.

## References
- https://jira.mongodb.org/browse/SERVER-49142
- https://nvd.nist.gov/vuln/detail/CVE-2020-7925
