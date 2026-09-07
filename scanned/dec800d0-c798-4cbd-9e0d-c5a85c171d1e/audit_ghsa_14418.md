# [M] Keycloak vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-w354-2f3c-qvg9
CVE: CVE-2022-1438
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-03-01
Source: https://github.com/advisories/GHSA-w354-2f3c-qvg9
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0

## Details
A flaw was found in Keycloak. Under specific circumstances, HTML entities are not sanitized during user impersonation, resulting in a Cross-site scripting (XSS) vulnerability.

## Details

This issue is the result of code found in the exception here: [https://github.com/keycloak/keycloak/blob/48835576daa158443f69917ac309e1a7c951bc87/services/src/main/java/org/keycloak/authentication/AuthenticationProcessor.java#L1045](https://github.com/keycloak/keycloak/blob/48835576daa158443f69917ac309e1a7c951bc87/services/src/main/java/org/keycloak/authentication/AuthenticationProcessor.java#L1045)

## Steps to reproduce

When using the legacy admin console:

1. Sign in as Admin user in first tab.
2. In that tab create new user in keycloak admin section > intercept user creation request and modify it by including malicious js script there (in username field).
3. Sign in as newly created user in second tab (same browser window but second tab).
4. Navigate back to first tab where you are signed in as admin, navigate to admin console which lists all application users.
5. Choose any user (except newly created malicious one) – modify anything for that user in his settings. E.g. navigate to credentials tab and set new credentials for him. Also set new password as temporary.
6. After update for that user is made, use impersonate option on that modified user.
7. You should see window with form which requires providing new credentials – fill it and submit request.
8. Just after submiting request user will get notified that “You are already authenticated as different user ‘[user + payload]’ in this session. Please sign out first.”  And malicious payload will be executed instantly.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-w354-2f3c-qvg9
- https://nvd.nist.gov/vuln/detail/CVE-2022-1438
- https://access.redhat.com/errata/RHSA-2023:1043
- https://access.redhat.com/errata/RHSA-2023:1044
- https://access.redhat.com/errata/RHSA-2023:1045
- https://access.redhat.com/errata/RHSA-2023:1047
- https://access.redhat.com/errata/RHSA-2023:1049
- https://access.redhat.com/security/cve/cve-2022-1438
- https://bugzilla.redhat.com/show_bug.cgi?id=2031904
- https://github.com/keycloak/keycloak
- https://github.com/keycloak/keycloak/blob/48835576daa158443f69917ac309e1a7c951bc87/services/src/main/java/org/keycloak/authentication/AuthenticationProcessor.java#L1045
