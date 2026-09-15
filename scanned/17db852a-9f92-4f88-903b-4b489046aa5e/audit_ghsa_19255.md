# [H] ZITADEL Allows IdP Intent Token Reuse

## Summary
Severity: High
Advisory: GHSA-g4r8-mp7g-85fq
CVE: CVE-2025-46815
CWE: CWE-294, CWE-384, CWE-613
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2025-05-06
Source: https://github.com/advisories/GHSA-g4r8-mp7g-85fq
Type: github-advisory

## Affected
- Go: `github.com/zitadel/zitadel` — affected >=3.0.0-rc.1 <3.0.0
- Go: `github.com/zitadel/zitadel` — affected >=0 <2.70.10
- Go: `github.com/zitadel/zitadel` — affected >=2.71.0 <2.71.9

## Details
### Impact

ZITADEL offers developers the ability to manage user sessions using the [Session API](https://zitadel.com/docs/category/apis/resources/session_service_v2/session-service). This API enables the use of IdPs for authentication, known as idp intents.

Following a successful idp intent, the client receives an id and token on a predefined URI. These id and token can then be used to authenticate the user or their session.

However, it was possible to exploit this feature by repeatedly using intents. This allowed an attacker with access to the application’s URI to retrieve the id and token, enabling them to authenticate on behalf of the user.

It’s important to note that the use of additional factors (MFA) prevents a complete authentication process and, consequently, access to the ZITADEL API.

### Patches

3.x versions are fixed on >=[3.0.0](https://github.com/zitadel/zitadel/releases/tag/v3.0.0)
2.71.x versions are fixed on >=[2.71.9](https://github.com/zitadel/zitadel/releases/tag/v2.71.9)
2.x versions are fixed on >=[2.70.10](https://github.com/zitadel/zitadel/releases/tag/v2.70.10)

### Workarounds

The recommended solution is to update ZITADEL to a patched version.

### Questions

If you have any questions or comments about this advisory, please email us at [security@zitadel.com](mailto:security@zitadel.com)

### Credits

Thanks to Józef Chraplewski from Nedap for reporting this vulnerability.

## References
- https://github.com/zitadel/zitadel/security/advisories/GHSA-g4r8-mp7g-85fq
- https://nvd.nist.gov/vuln/detail/CVE-2025-46815
- https://github.com/zitadel/zitadel/commit/b1e60e7398d677f08b06fd7715227f70b7ca1162
- https://github.com/zitadel/zitadel
- https://github.com/zitadel/zitadel/releases/tag/v2.70.10
- https://github.com/zitadel/zitadel/releases/tag/v2.71.9
- https://github.com/zitadel/zitadel/releases/tag/v3.0.0
