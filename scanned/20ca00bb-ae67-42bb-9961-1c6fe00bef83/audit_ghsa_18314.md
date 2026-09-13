# [M] Keycloak SMTP Inject Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-m4j5-5x4r-2xp9
CVE: CVE-2025-8419
CWE: CWE-93
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-09-17
Source: https://github.com/advisories/GHSA-m4j5-5x4r-2xp9
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0 <26.2.8
- Maven: `org.keycloak:keycloak-services` — affected >=26.3.0 <26.3.3

## Details
Special characters used during e-mail registration may perform SMTP Injection and unexpectedly send short unwanted e-mails. The email is limited to 64 characters (limited local part of the email), so the attack is limited to very shorts emails (subject and little data, the example is 60 chars). This flaw's only direct consequence is an unsolicited email being sent from the Keycloak server. However, this action could be a precursor for more sophisticated attacks.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-m4j5-5x4r-2xp9
- https://nvd.nist.gov/vuln/detail/CVE-2025-8419
- https://access.redhat.com/errata/RHSA-2025:15336
- https://access.redhat.com/errata/RHSA-2025:15337
- https://access.redhat.com/errata/RHSA-2025:15338
- https://access.redhat.com/errata/RHSA-2025:15339
- https://access.redhat.com/security/cve/CVE-2025-8419
- https://bugzilla.redhat.com/show_bug.cgi?id=2385776
- https://github.com/keycloak/keycloak
