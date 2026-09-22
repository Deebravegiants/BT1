# [H] Hermes WebUI < 0.51.409 - Unauthenticated Passkey Registration via Authentication Bypass

## Summary
Severity: High
Advisory: CVE-2026-55196
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-17
Source: https://osv.dev/vulnerability/CVE-2026-55196
Type: osv

## Details
Hermes WebUI before 0.51.409 contains an authentication bypass vulnerability in passkey registration endpoints that allows unauthenticated remote attackers to register arbitrary passkeys. When HERMES_WEBUI_PASSKEY=1 is enabled with no existing credentials, POST /api/auth/passkey/register/options and POST /api/auth/passkey/register endpoints are accessible without authentication, allowing attackers to claim the first passkey and gain permanent administrative control.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55196.json
- https://github.com/nesquena/hermes-webui/releases/tag/v0.51.442
- https://nvd.nist.gov/vuln/detail/CVE-2026-55196
- https://www.vulncheck.com/advisories/hermes-webui-unauthenticated-passkey-registration-via-authentication-bypass
- https://github.com/nesquena/hermes-webui/pull/4171
- https://github.com/nesquena/hermes-webui/pull/4267
- https://github.com/nesquena/hermes-webui/commit/4d90577e25d5537cb07290eca3fb8abff3bab316
- https://github.com/nesquena/hermes-webui
