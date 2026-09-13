# [C] Open WebUI: LDAP Empty Password Authentication Bypass

## Summary
Severity: Critical
Advisory: CVE-2026-44551
Aliases: GHSA-2r4p-jpmg-48f4, PYSEC-2026-435
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-05-15
Source: https://osv.dev/vulnerability/CVE-2026-44551
Type: osv

## Details
Open WebUI is a self-hosted artificial intelligence platform designed to operate entirely offline. Prior to 0.9.0, the LDAP authentication endpoint does not validate that the submitted password is non-empty before performing a Simple Bind against the LDAP server. The LdapForm Pydantic model accepts password: str with no minimum length constraint, so an empty string passes validation. The subsequent Connection.bind() call succeeds on vulnerable LDAP servers, and the application issues a full session token for the target user. This vulnerability is fixed in 0.9.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44551.json
- https://github.com/open-webui/open-webui/security/advisories/GHSA-2r4p-jpmg-48f4
- https://nvd.nist.gov/vuln/detail/CVE-2026-44551
