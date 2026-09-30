# [M] Coolify: Server-Side Request Forgery via attacker-controlled GitHub App API URL

## Summary
Severity: Medium
Advisory: CVE-2026-34170
Aliases: GHSA-3g6r-cxv5-3c7h
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/CVE-2026-34170
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. Prior to 4.0.0-beta.471, the GithubApp api_url field is used as the base URL for server-side HTTP requests without allowlisting or private IP blocking, allowing an authenticated user to configure a GitHub App source that causes Coolify to request internal services or cloud metadata endpoints. This issue is reported as fixed in version 4.0.0-beta.471.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34170.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-3g6r-cxv5-3c7h
- https://nvd.nist.gov/vuln/detail/CVE-2026-34170
