# [H] Quarkus has Authentication/Authorization bypasses

## Summary
Severity: High
Advisory: GHSA-rc95-pcm8-65v9
CVE: CVE-2026-39852
CWE: CWE-287, CWE-551, CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-rc95-pcm8-65v9
Type: github-advisory

## Affected
- Maven: `io.quarkus:quarkus-vertx-http` — affected >=0 <3.20.6.1
- Maven: `io.quarkus:quarkus-vertx-http` — affected >=3.21.0 <3.27.3.1
- Maven: `io.quarkus:quarkus-vertx-http` — affected >=3.30.0 <3.33.1.1
- Maven: `io.quarkus:quarkus-vertx-http` — affected >=3.34.0 <3.35.1.1

## Details
Quarkus version 3.32.4 is vulnerable to an authorization bypass issue (GHSL-2026-099), in which semicolons (matrix parameters) in HTTP requests can be used to bypass security constraints, potentially allowing unauthorized access to protected resources.

Unauthenticated or lower-privileged users can bypass HTTP path-based authorization policies by appending a semicolon (`;`) and arbitrary text to the request URL. The vulnerability arises from a path-normalization inconsistency: Quarkus's [security layer](https://quarkus.io/guides/security-authorize-web-endpoints-reference) performs authorization checks on the raw URL path (which preserves matrix parameters), whereas RESTEasy Reactive's routing layer strips matrix parameters before matching endpoints. This allows requests like `/api/admin;anything` to bypass policies protecting `/api/admin` while still routing to the protected endpoint.


### Impact

This issue may lead to Authentication/Authorization bypasses.

### Credits

This issue was discovered with the [GitHub Security Lab Taskflow Agent](https://github.com/GitHubSecurityLab/seclab-taskflow-agent) and manually verified by GHSL team members [@p- (Peter Stöckli)](https://github.com/p-) and [@m-y-mo (Man Yue Mo)](https://github.com/m-y-mo).

## References
- https://github.com/quarkusio/quarkus/security/advisories/GHSA-rc95-pcm8-65v9
- https://nvd.nist.gov/vuln/detail/CVE-2026-39852
- https://access.redhat.com/errata/RHSA-2026:11720
- https://access.redhat.com/errata/RHSA-2026:11721
- https://access.redhat.com/errata/RHSA-2026:13631
- https://access.redhat.com/errata/RHSA-2026:17789
- https://access.redhat.com/errata/RHSA-2026:25089
- https://access.redhat.com/errata/RHSA-2026:34608
- https://access.redhat.com/errata/RHSA-2026:54435
- https://access.redhat.com/security/cve/CVE-2026-39852
- https://bugzilla.redhat.com/show_bug.cgi?id=2457819
- https://github.com/quarkusio/quarkus
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-39852.json
