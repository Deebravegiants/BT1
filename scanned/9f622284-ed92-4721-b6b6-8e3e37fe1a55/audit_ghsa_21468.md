# [C] Code injection in quarkus dev ui config editor

## Summary
Severity: Critical
Advisory: GHSA-g56w-cwg4-hxx9
CVE: CVE-2022-4116
CWE: CWE-74, CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-11-22
Source: https://github.com/advisories/GHSA-g56w-cwg4-hxx9
Type: github-advisory

## Affected
- Maven: `io.quarkus:quarkus-vertx-http-deployment` — affected >=2.14.0 <2.14.2.Final
- Maven: `io.quarkus:quarkus-vertx-http-deployment` — affected >=0 <2.13.5.Final

## Details
A vulnerability was found in quarkus. This security flaw happens in Dev UI Config Editor which is vulnerable to drive-by localhost attacks leading to remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4116
- https://access.redhat.com/security/cve/CVE-2022-4116
- https://bugzilla.redhat.com/show_bug.cgi?id=2144748
- https://github.com/quarkusio/quarkus
- https://github.com/quarkusio/quarkus/discussions/29527
- https://github.com/quarkusio/quarkus/discussions/29527#discussioncomment-4387809
