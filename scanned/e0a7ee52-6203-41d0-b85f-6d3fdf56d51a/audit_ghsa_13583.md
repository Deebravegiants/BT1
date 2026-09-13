# [H] Quarkus OIDC can leak both ID and access tokens

## Summary
Severity: High
Advisory: GHSA-6hc9-cf8x-hf83
CVE: CVE-2023-1584
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-10-04
Source: https://github.com/advisories/GHSA-6hc9-cf8x-hf83
Type: github-advisory

## Affected
- Maven: `io.quarkus:quarkus-oidc` — affected >=0 <2.13.0.Final
- Maven: `io.quarkus:quarkus-oidc` — affected >=3.0.0 <3.1.0.Final

## Details
A flaw was found in Quarkus. Quarkus OIDC can leak both ID and access tokens in the authorization code flow when an insecure HTTP protocol is used, which can allow attackers to access sensitive user data directly from the ID token or by using the access token to access user data from OIDC provider services. Please note that passwords are not stored in access tokens.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-1584
- https://github.com/quarkusio/quarkus/pull/32192
- https://github.com/quarkusio/quarkus/pull/32192/commits/5369d7ff233d3afe84ecd9160c541fba52b38e69
- https://github.com/quarkusio/quarkus/pull/33414
- https://github.com/quarkusio/quarkus/pull/33414/commits/df305ff12386cf28b33567b8d9a18db164f019dd
- https://github.com/quarkusio/quarkus/commit/5369d7ff233d3afe84ecd9160c541fba52b38e69
- https://github.com/quarkusio/quarkus/commit/df305ff12386cf28b33567b8d9a18db164f019dd
- https://access.redhat.com/errata/RHSA-2023:3809
- https://access.redhat.com/errata/RHSA-2023:7653
- https://access.redhat.com/security/cve/CVE-2023-1584
- https://bugzilla.redhat.com/show_bug.cgi?id=2180886
- https://github.com/quarkusio/quarkus
