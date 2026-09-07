# [C] Authentication Bypass in github.com/russellhaering/gosaml2

## Summary
Severity: Critical
Advisory: GHSA-xhqq-x44f-9fgg
CVE: CVE-2020-29509
CWE: CWE-115
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-11
Source: https://github.com/advisories/GHSA-xhqq-x44f-9fgg
Type: github-advisory

## Affected
- Go: `github.com/russellhaering/gosaml2` — affected >=0 <0.6.0

## Details
### Impact
Given a valid SAML Response, it may be possible for an attacker to mutate the XML document in such a way that gosaml2 will trust a different portion of the document than was signed.

Depending on the implementation of the Service Provider this enables a variety of attacks, including users accessing accounts other than the one to which they authenticated in the Identity Provider, or full authentication bypass.

### Patches
Service Providers utilizing gosaml2 should upgrade to v0.6.0 or greater.

## References
- https://github.com/russellhaering/gosaml2/security/advisories/GHSA-xhqq-x44f-9fgg
- https://nvd.nist.gov/vuln/detail/CVE-2020-29509
- https://github.com/russellhaering/gosaml2/commit/42606dafba60c58c458f14f75c4c230459672ab9
- https://github.com/mattermost/xml-roundtrip-validator/blob/master/advisories/unstable-attributes.md
- https://pkg.go.dev/vuln/GO-2021-0060
- https://security.netapp.com/advisory/ntap-20210129-0006
