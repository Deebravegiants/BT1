# [M] SurrealDB bypass of deny-net flags via redirect results in server-side request forgery (SSRF)

## Summary
Severity: Medium
Advisory: GHSA-5q9x-554g-9jgg
CWE: CWE-918
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:L/VA:L/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2025-04-11
Source: https://github.com/advisories/GHSA-5q9x-554g-9jgg
Type: github-advisory

## Affected
- crates.io: `surrealdb` — affected >=2.2.0 <2.2.2
- crates.io: `surrealdb` — affected >=2.1.0 <2.1.5
- crates.io: `surrealdb` — affected >=0 <2.0.5

## Details
SurrealDB offers http functions that can access external network endpoints. A typical, albeit [not recommended ](https://surrealdb.com/docs/surrealdb/reference-guide/security-best-practices#example-deny-all-capabilities-with-some-exceptions) configuration would be to start SurrealDB with all network connections allowed with the exception of a deny list. For example, `surreal start --allow-net --deny-net 10.0.0.0/8` will allow all network connections except to the 10.0.0.0/8 block.

An authenticated user of SurrealDB can use redirects to bypass this restriction. For example by hosting a server on the public internet which redirects to the IP addresses blocked by the administrator of the SurrealDB server via HTTP 301 or 307 response codes. 

When sending SurrealDB statements containing the `http::*` functions to the attacker controlled host, the SurrealDB server will follow the redirects to the blocked IP address. Because the statements also return the responses to the attacker, this issue constitutes a full SSRF vulnerability.

This issue was discovered and patched during an code audit and penetration test of SurrealDB by cure53, the severity as defined within cure53's preliminary finding is Medium, matched by our CVSS v4 assessment.

### Impact

The impact of this vulnerability is circumvention of the `--deny-net` capability and resulting impact on systems external to SurrealDB. The ultimate impact is dependent on the deployment scenario. 

For example, if the SurrealDB server blocks requests to internal and private IP addresses because they run services which don't require authentication, such as AWS deployments using IMDSv1, the attacker can access these internal endpoints directly, and potentially retrieve or even alter sensitive information and credentials.

The circumvention could also be used to redirect traffic to the SurrealDB port, providing a low level of impact to availability. 

### Patches
A patch has been created that adds an HTTP redirect limit, and checks HTTP redirects against allowed network targets, preventing redirections to disallowed uri's.

- Versions 2.0.5, 2.1.5, 2.2.2 and later are not affected by this issue.

### Workarounds
The possibility of this vulnerability being exploited can be reduced by following an allowlist approach to enabling the http capability `surreal start --allow-net 10.0.0.0/8 ` or using the equivalent `SURREAL_CAPS_ALLOW_NET` environment variable,  where endpoints allowed are fully trusted and are not controlled by regular users.

The network access capability can be disabled, using `--deny-net` or the equivalent `SURREAL_CAPS_DENY_NET` environment variable without specifying targets, with impact to SurrealDB functionality.

As the impact of this vulnerability depends on the security of the deployment environment of SurrealDB, best practices should be followed within that environment.


### References
[#5597](https://github.com/surrealdb/surrealdb/pull/5597)
[SurrealDB Documentation - Environment Variables](https://surrealdb.com/docs/surrealdb/cli/env)
[SurrealDB Documentation - Capabilities](https://surrealdb.com/docs/surrealdb/security/capabilities)
[SurrealDB Documentation - Network Access Capability](https://surrealdb.com/docs/surrealdb/security/capabilities#network)

## References
- https://github.com/surrealdb/surrealdb/security/advisories/GHSA-5q9x-554g-9jgg
- https://github.com/surrealdb/surrealdb/pull/5597
- https://github.com/surrealdb/surrealdb
