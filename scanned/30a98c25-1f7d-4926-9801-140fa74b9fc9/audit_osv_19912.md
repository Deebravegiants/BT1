# [M] CVE-2021-27736

## Summary
Severity: Medium
Advisory: CVE-2021-27736
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-04-22
Source: https://osv.dev/vulnerability/CVE-2021-27736
Type: osv

## Details
FusionAuth fusionauth-samlv2 before 0.5.4 allows XXE attacks via a forged AuthnRequest or LogoutRequest because parseFromBytes uses javax.xml.parsers.DocumentBuilderFactory unsafely.

## References
- https://github.com/FusionAuth/fusionauth-samlv2/commit/c66fb689d50010662f705d5b585c6388ce555dbd
- https://github.com/FusionAuth/fusionauth-samlv2/compare/0.5.3...0.5.4
- https://www.compass-security.com/fileadmin/Research/Advisories/2021-03_CSNC-2021-004_FusionAuth_SAML_Library_XML_External_Entity.txt
