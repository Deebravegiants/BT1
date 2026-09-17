# [H] Allocation of Resources Without Limits in Keycloak

## Summary
Severity: High
Advisory: GHSA-54f3-c6hg-865h
CVE: CVE-2023-6563
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H (CVSS_V3)
Published: 2023-12-14
Source: https://github.com/advisories/GHSA-54f3-c6hg-865h
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-model-jpa` — affected >=0 <21.0.0

## Details
An unconstrained memory consumption vulnerability was discovered in Keycloak. It can be triggered in environments which have millions of offline tokens (> 500,000 users with each having at least 2 saved sessions). If an attacker creates two or more user sessions and then open the "consents" tab of the admin User Interface, the UI attempts to load a huge number of offline client sessions leading to excessive memory and CPU consumption which could potentially crash the entire system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-6563
- https://github.com/keycloak/keycloak/issues/13340
- https://github.com/keycloak/keycloak/pull/15463
- https://github.com/keycloak/keycloak/commit/556146f961f7c8ddf64de15e2117a58d045f72b5
- https://access.redhat.com/errata/RHSA-2023:7854
- https://access.redhat.com/errata/RHSA-2023:7855
- https://access.redhat.com/errata/RHSA-2023:7856
- https://access.redhat.com/errata/RHSA-2023:7857
- https://access.redhat.com/errata/RHSA-2023:7858
- https://access.redhat.com/security/cve/CVE-2023-6563
- https://bugzilla.redhat.com/show_bug.cgi?id=2253308
- https://github.com/keycloak/keycloak
