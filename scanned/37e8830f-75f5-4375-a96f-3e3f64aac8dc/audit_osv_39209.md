# [H] Medplum - Exposure of OAuth client secret via dynamic registration endpoint in self-hosted configurations

## Summary
Severity: High
Advisory: CVE-2026-44506
Aliases: GHSA-ch8p-j6cm-r7w5
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-44506
Type: osv

## Details
Medplum is a developer platform that enables development of healthcare apps. In Medplum versions 4.1.10 through 5.1.6, the /oauth2/register endpoint could return the client_secret of preconfigured OAuth clients defined via the defaultOAuthClients server configuration when a matching redirect_uri was provided. This issue has been patched in version 5.1.7.

## References
- https://github.com/medplum/medplum/releases/tag/v5.1.7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44506.json
- https://github.com/medplum/medplum/security/advisories/GHSA-ch8p-j6cm-r7w5
- https://nvd.nist.gov/vuln/detail/CVE-2026-44506
