# [M] n8n before 1.123.73 Credential Exposure via Error Logging

## Summary
Severity: Medium
Advisory: CVE-2026-85171
Aliases: GHSA-vrv8-j27g-g7cr
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85171
Type: osv

## Details
n8n before 1.123.73, 2.35.4, and 2.36.2 contains a credential exposure vulnerability in the Strapi, SeaTable, and Mailcheck nodes. These nodes send their decrypted credentials to the authentication endpoint via the raw legacy HTTP helper outside any error handling, causing the plaintext secret to be persisted in execution error data. Any authenticated user can read the plaintext secret from their own execution through the REST API, bypassing the blank-value redaction enforced by the credentials API.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85171.json
- https://github.com/n8n-io/n8n/security/advisories/GHSA-vrv8-j27g-g7cr
- https://nvd.nist.gov/vuln/detail/CVE-2026-85171
- https://www.vulncheck.com/advisories/n8n-before-1.123.73-credential-exposure-via-error-logging
