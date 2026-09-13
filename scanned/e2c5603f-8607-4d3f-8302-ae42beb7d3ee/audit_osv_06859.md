# [M] User may trigger invariant when allowed to send commands directly to shards

## Summary
Severity: Medium
Advisory: BIT-mongodb-2021-32037
Aliases: CVE-2021-32037
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mongodb-2021-32037
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=5.0.0 <5.0.3

## Details
An authorized user may trigger an invariant which may result in denial of service or server exit if a relevant aggregation request is sent to a shard. Usually, the requests are sent via mongos and special privileges are required in order to know the address of the shards and to log in to the shards of an auth enabled environment. This issue affects MongoDB Server v5.0 versions prior to and including 5.0.2.

## References
- https://jira.mongodb.org/browse/SERVER-59071
- https://nvd.nist.gov/vuln/detail/CVE-2021-32037
