# [M] etcd key name can be accessed via LeaseTimeToLive API

## Summary
Severity: Medium
Advisory: BIT-etcd-2023-32082
Aliases: CVE-2023-32082, GHSA-3p4g-rcw5-8298
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-etcd-2023-32082
Type: osv

## Affected
- Bitnami: `etcd` — affected >=3.5.0 <3.5.9

## Details
etcd is a distributed key-value store for the data of a distributed system. Prior to versions 3.4.26 and 3.5.9, the LeaseTimeToLive API allows access to key names (not value) associated to a lease when `Keys` parameter is true, even a user doesn't have read permission to the keys. The impact is limited to a cluster which enables auth (RBAC). Versions 3.4.26 and 3.5.9 fix this issue. There are no known workarounds.

## References
- https://github.com/etcd-io/etcd/blob/main/CHANGELOG/CHANGELOG-3.4.md
- https://github.com/etcd-io/etcd/blob/main/CHANGELOG/CHANGELOG-3.5.md
- https://github.com/etcd-io/etcd/pull/15656
- https://github.com/etcd-io/etcd/security/advisories/GHSA-3p4g-rcw5-8298
- https://nvd.nist.gov/vuln/detail/CVE-2023-32082
