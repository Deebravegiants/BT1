# [C] CVE-2019-14837

## Summary
Severity: Critical
Advisory: CVE-2019-14837
Aliases: GHSA-cf8f-w2c5-p5jr
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2020-01-07
Source: https://osv.dev/vulnerability/CVE-2019-14837
Type: osv

## Details
A flaw was found in keycloack before version 8.0.0. The owner of 'placeholder.org' domain can setup mail server on this domain and knowing only name of a client can reset password and then log in. For example, for client name 'test' the email address will be 'service-account-test@placeholder.org'.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-14837
- https://issues.jboss.org/browse/KEYCLOAK-10780
- https://github.com/keycloak/keycloak/commit/9a7c1a91a59ab85e7f8889a505be04a71580777f
