# [H] Coolify: Authenticated RCE via command injection in CA certificate management feature

## Summary
Severity: High
Advisory: CVE-2026-27957
Aliases: GHSA-7g97-c4xv-3cjx
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-27957
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. Prior to 4.0.0-beta.464, an authenticated command injection vulnerability in the CA Certificate management feature allows any authenticated user to execute arbitrary commands as the configured SSH user on the managed server host. As the SSH user typically would have to either be root or part of the docker group for Coolify to function as intended, this provides complete compromise of the managed server and associated docker containers. This vulnerability is fixed in 4.0.0-beta.464.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27957.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-7g97-c4xv-3cjx
- https://nvd.nist.gov/vuln/detail/CVE-2026-27957
