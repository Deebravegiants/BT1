# [M] Altair GraphQL Client's desktop app does not validate HTTPS certificates

## Summary
Severity: Medium
Advisory: CVE-2024-54147
Aliases: GHSA-8v9h-hxp5-9jcx
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2024-12-09
Source: https://osv.dev/vulnerability/CVE-2024-54147
Type: osv

## Details
Altair is a GraphQL client for all platforms. Prior to version 8.0.5, Altair GraphQL Client's desktop app does not validate HTTPS certificates allowing a man-in-the-middle to intercept all requests. Any Altair users on untrusted networks (eg. public wifi, malicious DNS servers) may have all GraphQL request and response headers and bodies fully compromised including authorization tokens. The attack also allows obtaining full access to any signed-in Altair GraphQL Cloud account and replacing payment checkout pages with a malicious website. Version 8.0.5 fixes the issue.

## References
- https://github.com/altair-graphql/altair/blob/004f645d1cae032787fccf7166dc193b775e9660/packages/altair-electron/src/app/index.ts#L162-L170
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/54xxx/CVE-2024-54147.json
- https://github.com/altair-graphql/altair/security/advisories/GHSA-8v9h-hxp5-9jcx
- https://nvd.nist.gov/vuln/detail/CVE-2024-54147
