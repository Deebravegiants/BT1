# [H] LightRAG: Hardcoded JWT Signing Secret Allows Authentication Bypass

## Summary
Severity: High
Advisory: GHSA-mcww-4hxq-hfr3
CVE: CVE-2026-30762
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-04
Source: https://github.com/advisories/GHSA-mcww-4hxq-hfr3
Type: github-advisory

## Affected
- PyPI: `lightrag-hku` — affected >=0 <1.4.13

## Details
Subject: Security Vulnerability Report Hardcoded JWT Secret (CVE-2026-30762)

Hi HKUDS team,

I'm writing to report a security vulnerability I discovered in LightRAG v1.4.10. This has been assigned CVE-2026-30762 by MITRE.

Vulnerability: Hardcoded JWT signing secret
Type: Improper Authentication (CWE-287)
Severity: High
Attack Vector: Remote / Unauthenticated

Summary:
The file lightrag/api/config.py (line 397) uses a default JWT secret "lightrag-jwt-default-secret" when the TOKEN_SECRET environment variable is not set. The AuthHandler in lightrag/api/auth.py (lines 24-25) uses this secret to sign and verify tokens. An unauthenticated attacker can forge valid JWT tokens using the publicly known default secret and gain access to any protected endpoint.

Reproduction:
1. Install LightRAG v1.4.10 with AUTH_ACCOUNTS configured but no TOKEN_SECRET set
2. Use PyJWT to sign a token: jwt.encode({"sub": "admin", "role": "user"}, "lightrag-jwt-default-secret", algorithm="HS256")
3. Send a request to any protected endpoint with the header: Authorization: Bearer <forged_token>
4. Access is granted without valid credentials

Suggested Fix:
Require TOKEN_SECRET to be explicitly set when AUTH_ACCOUNTS is configured. Refuse to start the API server if authentication is enabled but no custom secret is provided.

I'm following a 90-day responsible disclosure timeline from today's date. Please let me know if you have any questions or need additional information.

Best regards,
Venkata Avinash Taduturi

## References
- https://github.com/HKUDS/LightRAG/security/advisories/GHSA-mcww-4hxq-hfr3
- https://github.com/HKUDS/LightRAG
