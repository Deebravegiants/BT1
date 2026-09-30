# [H] TypeBot vulnerable to OpenAI API key exfiltration in listModels via attacker-controlled baseUrl

## Summary
Severity: High
Advisory: CVE-2026-48766
Aliases: GHSA-gc3v-9whw-6wjh
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:L)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-48766
Type: osv

## Details
TypeBot is a chatbot builder tool. Versions prior to 3.17.0 allow a low-privilege guest member of a workspace to exfiltrate stored OpenAI-compatible API keys by invoking the OpenAI model-listing helper with an attacker-controlled `baseUrl`. The vulnerable path decrypts the selected workspace credential, creates an OpenAI client with the secret in both `apiKey` and the explicit `api-key` header, and then sends the outbound request to the caller-supplied URL. Because the permission check accepts any readable workspace member and `listCredentials` reveals credential identifiers to guests, a guest can force the server to deliver the workspace secret to attacker infrastructure. Version 3.17.0 patches the issue.

## References
- https://github.com/baptisteArno/typebot.io/releases/tag/v3.17.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48766.json
- https://github.com/baptisteArno/typebot.io/security/advisories/GHSA-gc3v-9whw-6wjh
- https://nvd.nist.gov/vuln/detail/CVE-2026-48766
- https://github.com/baptisteArno/typebot.io/commit/7ae4c007d0987d2ca907b47e1b7418db62b8a157
- https://github.com/baptisteArno/typebot.io/pull/2459
