# [M] Keycloaks's One Time Passcode (OTP) is valid longer than expiration timeSeverity

## Summary
Severity: Medium
Advisory: GHSA-xmmm-jw76-q7vg
CVE: CVE-2024-7318
CWE: CWE-324
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-10-14
Source: https://github.com/advisories/GHSA-xmmm-jw76-q7vg
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-core` — affected >=0 <24.0.7
- Maven: `org.keycloak:keycloak-core` — affected >=25.0.0 <25.0.4

## Details
A vulnerability was found in Keycloak. Expired OTP codes are still usable when using FreeOTP when the OTP token period is set to 30 seconds (default). Instead of expiring and deemed unusable around 30 seconds in, the tokens are valid for an additional 30 seconds totaling 1 minute. A one time passcode that is valid longer than its expiration time increases the attack window for malicious actors to abuse the system and compromise accounts. Additionally, it increases the attack surface because at any given time, two OTPs are valid.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-xmmm-jw76-q7vg
- https://nvd.nist.gov/vuln/detail/CVE-2024-7318
- https://access.redhat.com/errata/RHSA-2024:6502
- https://access.redhat.com/errata/RHSA-2024:6503
- https://access.redhat.com/security/cve/CVE-2024-7318
- https://bugzilla.redhat.com/show_bug.cgi?id=2301876
- https://github.com/keycloak/keycloak
