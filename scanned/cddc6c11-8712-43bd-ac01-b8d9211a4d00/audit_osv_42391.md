# [H] OpenEMR 8.2.0 OAuth2 Password Grant Authentication Bypass via SMART Configuration

## Summary
Severity: High
Advisory: CVE-2026-67611
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-67611
Type: osv

## Details
OpenEMR through 8.2.0 contains an authentication bypass vulnerability that allows attackers with valid credentials to circumvent multi-factor authentication by exploiting the exposed OAuth2 password grant flow through an unauthenticated client registration endpoint. Attackers can register an OAuth2 client via the unauthenticated registration endpoint and use the password grant to exchange credentials for an API access token, bypassing the normal web interface authentication and any enforced multi-factor authentication controls.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67611.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-67611
- https://www.vulncheck.com/advisories/openemr-oauth2-password-grant-authentication-bypass-via-smart-configuration
- https://github.com/openemr/openemr
- https://jivasecurity.com/writeups/openemr-preauth-disclosure-password-grant
