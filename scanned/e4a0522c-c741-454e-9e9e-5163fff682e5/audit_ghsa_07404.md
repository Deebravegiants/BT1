# [H] Micronaut doesn't set a maximum redirect count for its HTTP Client, enabling infinite loop DoS

## Summary
Severity: High
Advisory: GHSA-387m-935m-c4vw
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-09
Source: https://github.com/advisories/GHSA-387m-935m-c4vw
Type: github-advisory

## Affected
- Maven: `io.micronaut:micronaut-http-client` — affected >=0 <3.10.7
- Maven: `io.micronaut:micronaut-http-client` — affected >=4.0.0-M1 <4.10.24
- Maven: `io.micronaut:micronaut-http-client` — affected >=5.0.0-M1 <5.0.1

## Details
The Netty-based Micronaut HTTP Client does not impose a limit on HTTP redirections, potentially allowing an infinite redirect loop that could lead to a denial-of-service attack.

### Patches

The following versions are patched: 

- For Micronaut 5, versions equal or greater than [5.0.1](https://github.com/micronaut-projects/micronaut-core/releases/v5.0.1) >=
- For Micronaut 4, versions equal or greater than [4.10.24](https://github.com/micronaut-projects/micronaut-core/releases/v4.10.24) >=
- For Micronaut 3, versions equal or greater than [3.10.7](https://github.com/micronaut-projects/micronaut-core/releases/v3.10.7) >=

### Workarounds
No

### Resources
Micronaut 5 Patch: https://github.com/micronaut-projects/micronaut-core/commit/6e88a972718d6e1521c5b3bb7766451798dba4e3
Micronaut 4 Patch: https://github.com/micronaut-projects/micronaut-core/commit/f1dffffec8fb5e3b7e94ae907ce0be3831e499d4
Micronaut 3 Patch: https://github.com/micronaut-projects/micronaut-core/commit/c06a2715ca7f78321bc3ca05f41cca78cd351320

## References
- https://github.com/micronaut-projects/micronaut-core/security/advisories/GHSA-387m-935m-c4vw
- https://github.com/micronaut-projects/micronaut-core/commit/6e88a972718d6e1521c5b3bb7766451798dba4e3
- https://github.com/micronaut-projects/micronaut-core/commit/c06a2715ca7f78321bc3ca05f41cca78cd351320
- https://github.com/micronaut-projects/micronaut-core/commit/f1dffffec8fb5e3b7e94ae907ce0be3831e499d4
- https://github.com/micronaut-projects/micronaut-core
