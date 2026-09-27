# [H] CVE-2024-42167

## Summary
Severity: High
Advisory: CVE-2024-42167
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-12
Source: https://osv.dev/vulnerability/CVE-2024-42167
Type: osv

## Details
The function "generate_app_certificates" in controllers/saml2/saml2.js of FIWARE Keyrock <= 8.4 does not neutralize special elements used in an OS Command properly. This allows an authenticated user with permissions to create applications to execute commands by creating an application with a malicious organisationname.

## References
- https://www.ait.ac.at/themen/cyber-security/pentesting/security-advisories
