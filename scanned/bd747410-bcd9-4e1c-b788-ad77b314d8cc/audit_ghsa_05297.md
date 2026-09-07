# [H] npm PraisonAI MCPSecurity Basic/OAuth authentication policies accept invalid credentials without validation

## Summary
Severity: High
Advisory: GHSA-4qq2-2j2x-x62c
CVE: CVE-2026-57134
CWE: CWE-287, CWE-288, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-4qq2-2j2x-x62c
Type: github-advisory

## Affected
- npm: `praisonai` — affected >=1.5.1 <1.7.2

## Details
## Summary

The published npm package `praisonai` exports an `MCPSecurity` helper described in source as:

```text
MCP Security - Authentication, authorization, and rate limiting
Provides security policies for MCP servers.
```

Its `AuthMethod` type advertises five authentication methods:

```ts
export type AuthMethod = 'none' | 'api-key' | 'bearer' | 'basic' | 'oauth';
```

The authentication-policy evaluator, however, only validates credentials for `api-key` and `bearer`:

```ts
if (policy.auth.method === 'api-key' || policy.auth.method === 'bearer') {
    const valid = policy.auth.validate
        ? await policy.auth.validate(token)
        : this.validateApiKey(token);

    if (!valid) {
        return { allowed: false, reason: 'Invalid credentials' };
    }
}

return { allowed: true, context: { authenticated: true } };
```

For `basic` and `oauth`, any non-empty `Authorization` header skips the supplied `validate` callback and returns allowed. A local PoV configures `auth.validate` to always return `false`; invalid `api-key` and `bearer` credentials are rejected, while invalid `basic` and `oauth` credentials are accepted without calling the validator.

This is a protection-mechanism failure in the exported npm MCP security helper. It is distinct from the separate issue that the npm `MCPServer` HTTP transport does not enforce authentication by default.

## Technical Details

`SecurityPolicy.auth` accepts both a method and a validator:

```ts
auth?: { method: AuthMethod; validate?: (token: string) => Promise<boolean> };
```

`extractToken()` parses both Bearer and Basic headers:

```ts
if (auth.startsWith('Bearer ')) {
    return auth.slice(7);
}
if (auth.startsWith('Basic ')) {
    return auth.slice(6);
}
return auth;
```

But `evaluatePolicy()` only calls `policy.auth.validate()` for two methods:

```ts
if (policy.auth.method === 'api-key' || policy.auth.method === 'bearer') {
    const valid = policy.auth.validate
        ? await policy.auth.validate(token)
        : this.validateApiKey(token);

    if (!valid) {
        return { allowed: false, reason: 'Invalid credentials' };
    }
}
```

There is no validation branch for `basic` or `oauth`. After extracting any non-empty token, those methods fall through to the success return:

```ts
return { allowed: true, context: { authenticated: true } };
```

`check()` then ignores successful authentication context and returns a generic allowed result:

```ts
return { allowed: true, context: { authenticated: false } };
```

That context propagation issue is secondary. The security-relevant flaw is that invalid Basic/OAuth credentials are allowed at all.

### Why This Is Not Intended Behavior

This is not a claim that every `MCPSecurity` user must choose Basic or OAuth. The issue is that the API explicitly exposes those methods as authentication methods and accepts a validator callback for the policy, but the implementation does not call the validator for those methods.

The control cases prove the intended security behavior:

- Missing Basic credentials are denied as `Authentication required`.
- Invalid `api-key` credentials are denied as `Invalid credentials`.
- Invalid `bearer` credentials are denied as `Invalid credentials`.

The only difference in the vulnerable cases is the selected advertised method. Invalid Basic/OAuth credentials should not become authenticated merely because the method is not listed in the two-method validation branch.

This also matches MCP authorization guidance. MCP servers acting as resource servers must validate received access tokens; receiving a token is not proof that it is valid or intended for the server.

## PoV

Run from a local reproduction checkout:

```bash
node poc/pov_poc.js 1.7.1
```

The PoV:

1. Installs `npm:praisonai@1.7.1` into a temporary project with scripts disabled.
2. Imports `MCPSecurity` from the package root.
3. Creates one `authenticate` policy per method.
4. Supplies an `auth.validate` callback that always returns `false`.
5. Sends invalid `api-key`, `bearer`, `basic`, and `oauth` credentials.
6. Confirms the missing-header Basic control is still denied.

Observed output summary from `evidence/pov-npm-1.7.1.json`:

```json
{
  "package": "praisonai",
  "version": "1.7.1",
  "cases": [
    {
      "method": "api-key",
      "validateCalls": 1,
      "allowed": false,
      "reason": "Invalid credentials"
    },
    {
      "method": "bearer",
      "validateCalls": 1,
      "allowed": false,
      "reason": "Invalid credentials"
    },
    {
      "method": "basic",
      "validateCalls": 0,
      "allowed": true
    },
    {
      "method": "oauth",
      "validateCalls": 0,
      "allowed": true
    },
    {
      "method": "basic",
      "authorizationHeaderPresent": false,
      "validateCalls": 0,
      "allowed": false,
      "reason": "Authentication required"
    }
  ],
  "controlsPass": true,
  "vulnerable": true
}
```

The PoV is local-only. It does not start a server, contact a third-party target, or use live credentials.

## PoC

The PoV section above contains the local reproduction command, input, and decisive output.

## Impact

A downstream application that uses `MCPSecurity` to protect an HTTP MCP transport, gateway, or equivalent tool/resource endpoint can believe it has enabled Basic or OAuth authentication while accepting any non-empty `Authorization` header.

Depending on the protected MCP tools and resources, this can allow an unauthenticated network caller to:

- list protected tools or resources;
- call tools that were intended to require authentication;
- read protected MCP resources;
- trigger agent/workflow actions exposed behind the security helper; and
- bypass audit assumptions based on the configured validator.

This report does not claim that npm PraisonAI wires `MCPSecurity` into the default `MCPServer.startHttp()` path. It is a library-level authentication bypass in an exported security component intended to protect MCP servers.

### Severity

Suggested severity: High.

Rationale:

- `AV`: the affected helper is intended to protect MCP server requests and equivalent HTTP security checks.
- `AC`: a single non-empty Basic or OAuth-style Authorization header is sufficient when such a policy is configured.
- `PR`: the bypass grants access without valid credentials.
- `UI`: no maintainer or user interaction is required after deployment.
- `S`: impact is within the PraisonAI-hosting service and its exposed MCP resources/tools.
- `C`: protected MCP resources or tool outputs may be disclosed.
- `I`: protected tool calls may perform state-changing actions depending on the registered tools; the score is conservative because the vulnerable helper is library-level and deployment-dependent.
- `A`: the PoV does not demonstrate availability impact.

If a deployment protects high-impact write or execution tools with `MCPSecurity`, maintainers may reasonably score integrity higher.

## Suggested Fix

Make authentication evaluation fail closed for every advertised method.

Recommended:

1. For `authenticate` policies, call `policy.auth.validate(token)` whenever it is provided, regardless of `auth.method`.
2. If no validator is provided, only fall back to `validateApiKey()` for `api-key` when that behavior is explicitly intended.
3. For `bearer` and `oauth`, require a validator or a server-side token validation implementation; otherwise deny with a configuration error.
4. For `basic`, decode the Basic credential safely and pass the decoded username/password or raw credential to a validator; if no validator exists, deny.
5. Treat unknown or unsupported methods as denied, not allowed.
6. Return authenticated context from `check()` after a successful authenticate policy instead of replacing it with `{ authenticated: false }`.
7. Add regression tests proving invalid credentials are rejected for `api-key`, `bearer`, `basic`, and `oauth`, and that each configured validator is called.

Minimal fail-closed shape:

```ts
if (policy.type === 'authenticate') {
  if (!policy.auth) return { allowed: false, reason: 'Authentication policy is not configured' };

  const token = request.headers ? this.extractToken(request.headers) : null;
  if (!token) return { allowed: false, reason: 'Authentication required' };

  if (policy.auth.validate) {
    const valid = await policy.auth.validate(token);
    return valid
      ? { allowed: true, context: { authenticated: true } }
      : { allowed: false, reason: 'Invalid credentials' };
  }

  if (policy.auth.method === 'api-key') {
    return this.validateApiKey(token)
      ? { allowed: true, context: { authenticated: true } }
      : { allowed: false, reason: 'Invalid credentials' };
  }

  return { allowed: false, reason: 'Authentication validator required' };
}
```

## Affected Package/Versions

- Repository: `MervinPraison/PraisonAI`
- Ecosystem: `npm`
- Package: `praisonai`
- Component: TypeScript MCP security helper `src/praisonai-ts/src/mcp/security.ts`
- Published dist path: `node_modules/praisonai/dist/mcp/security.js`
- Latest npm package validated: `1.7.1`
- Current `origin/main` validated: `1ad58ca02975ff1398efeda694ea2ab78f20cf3e`
- `src/praisonai-ts/package.json` at `origin/main`: `praisonai` `1.7.1`

Suggested affected range:

```text
npm:praisonai >= 1.5.1, <= 1.7.1
```

All published npm `1.x` versions were swept locally:

- `1.0.0` through `1.5.0`: the tested root export was unavailable or `MCPSecurity` was not exported as a constructor.
- `1.5.1`, `1.5.2`, `1.5.3`, `1.5.4`, `1.6.0`, `1.7.0`, and `1.7.1`: vulnerable.

The package root re-exports this helper:

```ts
export {
  MCPClient, createMCPClient, getMCPTools,
  MCPServer, createMCPServer,
  MCPSession as MCPSessionManager, createMCPSession,
  MCPSecurity, createMCPSecurity, createApiKeyPolicy, createRateLimitPolicy,
  type MCPClientConfig, type MCPSession, type MCPTransportType,
  type MCPServerConfig, type MCPServerTool,
  type SecurityPolicy, type SecurityResult
} from './mcp';
```

## Advisory History

Visible PraisonAI advisories and prior submissions were checked. The closest public advisory is `GHSA-98f9-fqg5-hvq5` / `CVE-2026-34953`, but that issue is distinct:

- `GHSA-98f9-fqg5-hvq5` affects the PyPI package and Python `OAuthManager.validate_token()`.
- This report affects the npm package and TypeScript `src/praisonai-ts/src/mcp/security.ts`.
- The prior issue accepts arbitrary Bearer tokens because an empty Python token store falls through to `True`.
- This issue accepts invalid Basic/OAuth credentials because the TypeScript validator callback is never called for those advertised methods.
- The affected ranges and patched surfaces are different.

The earlier npm `MCPServer` report is also distinct: it covers missing auth in the HTTP transport by default. This report covers a fail-open branch in the separate exported `MCPSecurity` helper when users attempt to add Basic/OAuth authentication.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-4qq2-2j2x-x62c
- https://github.com/MervinPraison/PraisonAI
