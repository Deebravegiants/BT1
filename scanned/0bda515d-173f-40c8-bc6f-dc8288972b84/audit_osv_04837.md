# [H] etcd: gRPC client listener does not enforce `--client-crl-file` certificate revocation

## Summary
Severity: High
Advisory: BIT-etcd-2026-59818
Aliases: CVE-2026-59818, GHSA-3wh4-j44w-pg92
Ecosystem: Bitnami
Published: 2026-07-14
Source: https://osv.dev/vulnerability/BIT-etcd-2026-59818
Type: osv

## Affected
- Bitnami: `etcd` — affected >=3.6.0 <3.6.13

## Details
etcd is a distributed key-value store for the data of a distributed system. Prior to 3.5.32 and 3.6.13, when etcd is configured with --listen-client-http-urls to split HTTP and gRPC client endpoints onto separate listeners, the --client-crl-file Certificate Revocation List is not enforced on the gRPC listener, allowing a client with a revoked certificate to authenticate successfully over gRPC. This issue is fixed in versions 3.5.32 and 3.6.13.

## References
- https://github.com/etcd-io/etcd/commit/2308ce1578064641d4d67c40f0487309267d1bef
- https://github.com/etcd-io/etcd/commit/24838af5a53dd0245adced920e42a9bf0e7a267f
- https://github.com/etcd-io/etcd/commit/8221ae82bc25d4d55ca64382207b69be71038cbb
- https://github.com/etcd-io/etcd/pull/22007
- https://github.com/etcd-io/etcd/pull/22021
- https://github.com/etcd-io/etcd/pull/22025
- https://github.com/etcd-io/etcd/releases/tag/v3.5.32
- https://github.com/etcd-io/etcd/releases/tag/v3.6.13
- https://github.com/etcd-io/etcd/security/advisories/GHSA-3wh4-j44w-pg92
- https://nvd.nist.gov/vuln/detail/CVE-2026-59818
