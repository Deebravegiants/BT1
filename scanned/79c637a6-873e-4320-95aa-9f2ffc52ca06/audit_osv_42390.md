# [H] OpenEMR 8.2.0 OAuth2 Dynamic Client Registration Unauthorized FHIR Access

## Summary
Severity: High
Advisory: CVE-2026-67610
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-67610
Type: osv

## Details
OpenEMR through 8.2.0 contains an improper authentication vulnerability in the OAuth2 dynamic client registration endpoint that allows unauthenticated attackers to register a malicious client with system-level FHIR scopes by supplying a self-generated RSA keypair via the jwks field. Once an administrator approves the registered client, attackers can use the client_credentials grant with a self-signed JWT assertion to obtain access tokens granting read access to all FHIR resources across all patients in the system.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67610.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-67610
- https://www.vulncheck.com/advisories/openemr-oauth2-dynamic-client-registration-unauthorized-fhir-access
- https://github.com/openemr/openemr
- https://jivasecurity.com/writeups/openemr-unauth-oauth2-client-registration
