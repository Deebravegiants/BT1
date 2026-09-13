# [M] Improper authorization in Keycloak

## Summary
Severity: Medium
Advisory: GHSA-f32v-vf79-p29q
CVE: CVE-2022-1466
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-04-27
Source: https://github.com/advisories/GHSA-f32v-vf79-p29q
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-core` — affected >=0 <17.0.1

## Details
Due to improper authorization, Red Hat Single Sign-On is vulnerable to users performing actions that they should not be allowed to perform. It was possible to add users to the master realm even though no respective permission was granted.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-1466
- https://bugzilla.redhat.com/show_bug.cgi?id=2050228
- https://github.com/keycloak/keycloak
- https://www.syss.de/fileadmin/dokumente/Publikationen/Advisories/SYSS-2021-076.txt
- https://www.syss.de/pentest-blog/fehlerhafte-autorisierung-bei-red-hat-single-sign-on-750ga-syss-2021-076
