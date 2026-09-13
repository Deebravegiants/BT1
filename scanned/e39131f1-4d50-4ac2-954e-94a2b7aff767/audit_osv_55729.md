# [M] SurrealDB allows bypass of deny-net flags via DNS resolution

## Summary
Severity: Medium
Advisory: GHSA-m3c3-78fh-w3w7
Aliases: CVE-2025-71390
Ecosystem: crates.io
Published: 2026-09-04
Source: https://osv.dev/vulnerability/GHSA-m3c3-78fh-w3w7
Type: osv

## Affected
- crates.io: `SurrealDB` — affected >=2.1.0 <2.1.8
- crates.io: `SurrealDB` — affected >=2.2.0 <2.2.6
- crates.io: `SurrealDB` — affected >=3.0.0-alpha.1 <3.0.0-alpha.7
- crates.io: `SurrealDB` — affected >=2.3.0 <2.3.6

## Details
SurrealDB offers http functions that can access external network endpoints. A typical, albeit [not recommended ](https://surrealdb.com/docs/surrealdb/reference-guide/security-best-practices#example-deny-all-capabilities-with-some-exceptions)configuration would be to start SurrealDB with all network connections allowed with the exception of a deny list. For example, `surreal start --allow-net --deny-net 10.0.0.0/8` will allow all network connections except to the 10.0.0.0/8 block.

An authenticated user of SurrealDB can use bypass this restriction, using `http::<fn>(<url>)` functions where the hostname resolves to an IP within the `--deny-net` block. For example if a SurrealDB administrator wanted to restrict access to other services within a private network and thus set the `--deny-net` to a network IP range, this could be circumvented by an attacker leveraging DNS records and hostname resolution. 

When sending SurrealDB statements containing the `http::*` functions, if the hostname resolves to a forbidden IP, the SurrealDB server will still issue the request and return the responses to the attacker.


### Impact
The impact of this vulnerability is circumvention of the `--deny-net` capability and resulting impact on systems external to SurrealDB. The ultimate impact is dependent on the deployment scenario.

For example, if the SurrealDB server blocks requests to internal/private IP addresses because those services don’t require authentication, but an attacker can still use SurrealDBs ability to resolve their hostnames via DNS and invoke them directly using `http::<fn>(<url>)`, the attacker can access these internal endpoints directly, and potentially retrieve or even alter sensitive information and credentials.

### Patches
A patch has been created that checks resolved hostnames against allowed network targets, preventing `http::*` functions from connecting to disallowed IPs.

- Versions 2.2.6, 2.3.6 and later are not affected by this issue. 
- The first release following 2.1.7 and 3.0.0-alpha.7 and later will not be affected by this issue

### Workarounds
The possibility of this vulnerability being exploited can be reduced by following an allowlist approach to enabling the http capability surreal start `--allow-net 10.0.0.0/8` or using the equivalent `SURREAL_CAPS_ALLOW_NET` environment variable, where endpoints allowed are fully trusted and are not controlled by regular users.

Alternatively, the network access capability can be disabled, using `--deny-net` or the equivalent `SURREAL_CAPS_DENY_NET` environment variable without specifying targets, which disables all outbound HTTP, with impact to SurrealDB functionality.

As the impact of this vulnerability depends on the security of the deployment environment of SurrealDB, best practices should be followed within that environment.

## References
- https://github.com/surrealdb/surrealdb/security/advisories/GHSA-m3c3-78fh-w3w7
- https://nvd.nist.gov/vuln/detail/CVE-2025-71390
- https://github.com/surrealdb/surrealdb/pull/6101
- https://github.com/surrealdb/surrealdb/pull/6119
- https://github.com/surrealdb/surrealdb/pull/6120
- https://github.com/surrealdb/surrealdb/pull/6121
- https://github.com/surrealdb/surrealdb/commit/4b317d850c7dabaee228144423741097232f7955
- https://github.com/surrealdb/surrealdb/commit/7c574dfa90211923e2ff1b12510c8479f8805b3d
- https://github.com/surrealdb/surrealdb/commit/b80d7d08b043c0e4bc0b7ff8ddb9be0907c0bf59
- https://github.com/surrealdb/surrealdb/commit/d5dc46f1c255ed450b3af025a0bdc165b6ce54a3
- https://github.com/surrealdb/surrealdb
- https://www.vulncheck.com/advisories/surrealdb-before-deny-net-bypass-via-dns-resolution
