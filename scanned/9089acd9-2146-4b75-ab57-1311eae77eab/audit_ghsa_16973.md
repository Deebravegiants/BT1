# [H] quarkus-core leaks local environment variables from Quarkus namespace during application's build

## Summary
Severity: High
Advisory: GHSA-f8h5-v2vg-46rr
CVE: CVE-2024-2700
CWE: CWE-526
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-04-04
Source: https://github.com/advisories/GHSA-f8h5-v2vg-46rr
Type: github-advisory

## Affected
- Maven: `io.quarkus:quarkus-core` — affected >=3.9.0.CR1 <3.9.2
- Maven: `io.quarkus:quarkus-core` — affected >=3.3.0.CR1 <3.8.4
- Maven: `io.quarkus:quarkus-core` — affected >=0 <3.2.12.Final

## Details
A vulnerability was found in the quarkus-core component. Quarkus captures the local environment variables from the Quarkus namespace during the application's build. Thus, running the resulting application inherits the values captured at build time. 

However, some local environment variables may have been set by the developer / CI environment for testing purposes, such as dropping the database during the application startup or trusting all TLS certificates to accept self-signed certificates. If these properties are configured using environment variables or the .env facility, they are captured into the built application. It may lead to dangerous behavior if the application does not override these values.

This behavior only happens for configuration properties from the `quarkus.*` namespace. So, application-specific properties are not captured.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-2700
- https://github.com/quarkusio/quarkus/issues/39927
- https://github.com/quarkusio/quarkus/commit/2b24dc8dbc8f390c97428783d67614418676fc2e
- https://github.com/quarkusio/quarkus/commit/91c3a58eaefe59e0afd430653d1636d664bd593f
- https://github.com/quarkusio/quarkus/commit/990c3ee5dd5c689f514e5e87c221bce6d5dff267
- https://access.redhat.com/errata/RHSA-2024:11023
- https://access.redhat.com/errata/RHSA-2024:2106
- https://access.redhat.com/errata/RHSA-2024:2705
- https://access.redhat.com/errata/RHSA-2024:3527
- https://access.redhat.com/errata/RHSA-2024:4028
- https://access.redhat.com/errata/RHSA-2024:4873
- https://access.redhat.com/security/cve/CVE-2024-2700
- https://bugzilla.redhat.com/show_bug.cgi?id=2273281
- https://github.com/quarkusio/quarkus
- https://quarkus.io/blog/quarkus-3-2-12-final-released
- https://quarkus.io/blog/quarkus-3-8-4-released
