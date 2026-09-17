# [M] Speckle Server API Token Privilege Escalation

## Summary
Severity: Medium
Advisory: CVE-2023-50713
Aliases: GHSA-xpf3-5q5x-3qwh
CVSS: 6.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:L/I:H/A:N)
Published: 2023-12-14
Source: https://osv.dev/vulnerability/CVE-2023-50713
Type: osv

## Details
Speckle Server provides server, frontend, 3D viewer, and other JavaScript utilities for the Speckle 3D data platform. A vulnerability in versions prior to 2.17.6 affects users who: authorized an application which requested a 'token write' scope or, using frontend-2, created a Personal Access Token (PAT) with `token write` scope. When creating a new token an agent needs to authorise the request with an existing token (the 'requesting token').  The requesting token is required to have token write scope in order to generate new tokens. However, Speckle server was not verifying that other privileges granted to the new token were not in excess of the privileges of the requesting token. A malicious actor could use a token with only token write scope to subsequently generate further tokens with additional privileges. These privileges would only grant privileges up to the existing privileges of the user. This vulnerability cannot be used to escalate a user's privileges or grant privileges on behalf of other users.

This has been patched as of version 2.17.6. All operators of Speckle servers should upgrade their server to version 2.17.6 or higher. Any users who authorized an application with 'token write' scope, or created a token in frontend-2 with `token write` scope should review existing tokens and permanently revoke any they do not recognize, revoke existing tokens and create new tokens, and review usage of their account for suspicious activity. No known workarounds for this issue exist.

## References
- https://github.com/specklesystems/speckle-server/releases/tag/2.17.6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/50xxx/CVE-2023-50713.json
- https://github.com/specklesystems/speckle-server/security/advisories/GHSA-xpf3-5q5x-3qwh
- https://nvd.nist.gov/vuln/detail/CVE-2023-50713
- https://github.com/specklesystems/speckle-server/commit/3689e1cd58ec4f06abee836af34889d6ce474571
