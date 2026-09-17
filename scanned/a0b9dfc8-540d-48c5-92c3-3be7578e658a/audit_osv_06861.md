# [H] Large aggregation pipelines with a specific stage can crash mongod under default configuration

## Summary
Severity: High
Advisory: BIT-mongodb-2021-32040
Aliases: CVE-2021-32040
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mongodb-2021-32040
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=5.0.0 <5.0.4

## Details
It may be possible to have an extremely long aggregation pipeline in conjunction with a specific stage/operator and cause a stack overflow due to the size of the stack frames used by that stage. If an attacker could cause such an aggregation to occur, they could maliciously crash MongoDB in a DoS attack. This vulnerability affects MongoDB Server v4.4 versions prior to and including 4.4.28, MongoDB Server v5.0 versions prior to 5.0.4 and MongoDB Server v4.2 versions prior to 4.2.16.

Workaround: >= v4.2.16 users and all v4.4 users can add the --setParameter internalPipelineLengthLimit=50 instead of the default 1000 to mongod at startup to prevent a crash.

## References
- https://jira.mongodb.org/browse/SERVER-58203
- https://jira.mongodb.org/browse/SERVER-59299
- https://jira.mongodb.org/browse/SERVER-60218
- https://security.netapp.com/advisory/ntap-20220609-0005/
- https://nvd.nist.gov/vuln/detail/CVE-2021-32040
