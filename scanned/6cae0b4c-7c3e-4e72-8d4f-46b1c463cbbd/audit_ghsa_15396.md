# [M] Openshift Console insufficient entropy vulnerability

## Summary
Severity: Medium
Advisory: GHSA-4crf-28c7-v4gr
CVE: CVE-2024-6508
CWE: CWE-331
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-08-21
Source: https://github.com/advisories/GHSA-4crf-28c7-v4gr
Type: github-advisory

## Affected
- Go: `github.com/openshift/console` — affected >=0

## Details
An insufficient entropy vulnerability was found in the Openshift Console. In the authorization code type and implicit grant type, the OAuth2 protocol is vulnerable to a Cross-Site Request Forgery (CSRF) attack if the state parameter is used inefficiently. This flaw allows logging into the victim’s current application account using a third-party account without any restrictions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-6508
- https://access.redhat.com/errata/RHSA-2024:10813
- https://access.redhat.com/errata/RHSA-2024:7922
- https://access.redhat.com/errata/RHSA-2024:8415
- https://access.redhat.com/errata/RHSA-2024:8991
- https://access.redhat.com/errata/RHSA-2024:9620
- https://access.redhat.com/errata/RHSA-2025:0014
- https://access.redhat.com/security/cve/CVE-2024-6508
- https://bugzilla.redhat.com/show_bug.cgi?id=2295777
- https://github.com/openshift/console
