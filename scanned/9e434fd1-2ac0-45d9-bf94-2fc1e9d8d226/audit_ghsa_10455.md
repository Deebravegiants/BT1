# [M] LobeHub: Unauthenticated authentication bypass on `webapi` routes via forgeable `X-lobe-chat-auth` header

## Summary
Severity: Medium
Advisory: GHSA-5mwj-v5jw-5c97
CVE: CVE-2026-39411
CWE: CWE-287, CWE-290, CWE-345
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-5mwj-v5jw-5c97
Type: github-advisory

## Affected
- npm: `@lobehub/lobehub` — affected >=0 <2.1.48

## Details
# Summary

The `webapi` authentication layer trusts a client-controlled `X-lobe-chat-auth` header that is only XOR-obfuscated, not signed or otherwise authenticated. Because the XOR key is hardcoded in the repository, an attacker can forge arbitrary auth payloads and bypass authentication on protected `webapi` routes.

Affected routes include:
- `POST /webapi/chat/[provider]`
- `GET /webapi/models/[provider]`
- `POST /webapi/models/[provider]/pull`
- `POST /webapi/create-image/comfyui`

## Details

The frontend creates `X-lobe-chat-auth` by XOR-obfuscating JSON with the static key `LobeHub · LobeHub`, and the backend reverses that operation and treats the decoded JSON as trusted authentication data.

The backend then accepts any truthy `apiKey` field in that decoded payload as sufficient authentication. No real API key validation is performed in this path.

As a result, an unauthenticated attacker can forge payloads such as:

```json
{"apiKey":"x"} 
```

or 

``` {"userId":"victim-user-123","apiKey":"x"} ```

and access webapi routes as an authenticated user.

Confirmed PoC
The following forged header was generated directly from the published XOR key using payload {"apiKey":"x"}:


``` X-lobe-chat-auth: N00DFSE+B1ngjQI0TR8= ```

That header decodes server-side to:

``` {"apiKey":"x"}```

A simple request is:

``` curl 'https://TARGET/webapi/models/openai' \
  -H 'X-lobe-chat-auth: N00DFSE+B1ngjQI0TR8=' ``` 

If the deployment has OPENAI_API_KEY configured, the request should succeed without a real login and return the provider model list.

A forged impersonation payload also works conceptually:

``` {"userId":"victim-user-123","apiKey":"x"} ``` 

### Impact
This is an unauthenticated authentication bypass.

An attacker can:

1. access protected webapi routes without a valid session
2. spend the deployment's server-side model provider credentials when env keys like OPENAI_API_KEY are configured
3. impersonate another user's userId for routes that load per-user provider configuration
4. invoke privileged backend model operations such as chat, model listing, model pulls, and ComfyUI image generation

### Root Cause
The core issue is trusting unsigned client-supplied auth data:

1. the auth header is only obfuscated, not authenticated
2. the obfuscation key is hardcoded and recoverable from the repository
3. the decoded apiKey field is treated as sufficient authentication even though it is never validated in this code path
4. Suggested Remediation
5. Stop treating X-lobe-chat-auth as an authentication token.
6. Remove the apiKey truthiness check as an auth decision.
7. Require a real server-validated session, OIDC token, or validated API key for all protected webapi routes.
8. If a client payload is still needed, sign it server-side with an HMAC or replace it with a normal session-bound backend lookup.
9. Affected Products

Ecosystem: npm

Package name: @lobehub/lobehub
Affected versions: <= 2.1.47
Patched versions: 2.1.48

Severity
Moderate
Vector String
CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:L

Weaknesses
CWE-287: Improper Authentication
CWE-345: Insufficient Verification of Data Authenticity
CWE-290: Authentication Bypass by Spoofing

## References
- https://github.com/lobehub/lobehub/security/advisories/GHSA-5mwj-v5jw-5c97
- https://nvd.nist.gov/vuln/detail/CVE-2026-39411
- https://github.com/lobehub/lobehub/pull/13535
- https://github.com/lobehub/lobehub/commit/3327b293d66c013f076cbc16cdbd05a61a3d0428
- https://github.com/lobehub/lobehub
- https://github.com/lobehub/lobehub/releases/tag/v2.1.48
