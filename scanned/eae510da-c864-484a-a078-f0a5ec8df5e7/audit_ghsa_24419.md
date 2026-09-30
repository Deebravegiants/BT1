# [H] Injection in Jolokia agent

## Summary
Severity: High
Advisory: GHSA-rhqj-4pp8-vvgf
CVE: CVE-2018-1000130
CWE: CWE-74
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-rhqj-4pp8-vvgf
Type: github-advisory

## Affected
- Maven: `org.jolokia:jolokia-core` — affected >=1.3.7 <1.5.0

## Details
A JNDI Injection vulnerability exists in Jolokia agent version 1.3.7 in the proxy mode that allows a remote attacker to run arbitrary Java code on the server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000130
- https://github.com/rhuss/jolokia/commit/1b360b8889f0ed51165a8d1ac55dd8e0aa2dfd4a
- https://github.com/rhuss/jolokia/commit/fd7b93da30c61a45bac10d8b311f1b79a74910f5
- https://access.redhat.com/errata/RHSA-2018:2669
- https://github.com/rhuss/jolokia
- https://github.com/rhuss/jolokia/releases/tag/v1.5.0
- https://jolokia.org/#Security_fixes_with_1.5.0
