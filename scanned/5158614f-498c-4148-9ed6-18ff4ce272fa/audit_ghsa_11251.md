# [H] OpenClaw: Gateway operator.write Can Reach Admin-Class Channel Allowlist Persistence via chat.send

## Summary
Severity: High
Advisory: GHSA-94pw-c6m8-p9p9
CVE: CVE-2026-35621
CWE: CWE-269
Ecosystem: npm
Published: 2026-03-30
Source: https://github.com/advisories/GHSA-94pw-c6m8-p9p9
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.24

## Details
> Fixed in OpenClaw 2026.3.24, the current shipping release.

## Summary

The shared `/allowlist` command persists channel authorization config through `writeConfigFile(...)` but does not re-validate gateway client scopes for internal gateway callers. Because `chat.send` is intentionally reachable to `operator.write` callers and still creates a generic command-authorized internal context, an authenticated write-scoped gateway client can indirectly mutate channel `allowFrom` and `groupAllowFrom` policy that direct `config.patch` correctly reserves to `operator.admin`.

This is not just a generic code smell. The current code already shows the intended boundary by adding sink-side internal admin checks to shared `/config` and `/plugins` writes, but `/allowlist` was left behind.

## Details

The gateway's documented scope split is clear:

- `chat.send` is a write-scoped action.
- direct config mutation is an admin-scoped action.

The vulnerable path is:

1. A gateway client authenticates with `operator.write`.
2. The client calls `chat.send`, which is intentionally allowed for that scope.
3. `chat.send` builds an internal message context with `CommandAuthorized: true` and carries `GatewayClientScopes` into the reply pipeline.
4. `resolveCommandAuthorization(...)` converts that internal message into `isAuthorizedSender=true` in the common case where no stricter `commands.allowFrom` override is configured.
5. `/allowlist add|remove` accepts that generic command authorization and proceeds into its config-backed edit path.
6. The handler clones the parsed config, calls `plugin.allowlist.applyConfigEdit(...)`, validates the result, and persists it with `writeConfigFile(validated.config)`.
7. No sink-side check requires `operator.admin` before the persistent write occurs.

That creates a direct control-plane mismatch:

- `config.patch` rejects the same caller with `missing scope: operator.admin`.
- `/allowlist add dm ...` or `/allowlist add group ...` reached through `chat.send` can still rewrite channel authorization state.

## Impact

- A gateway client intentionally limited to `operator.write` can persist first-party channel authorization policy.
- The caller can widen DM or group allowlists for channels using the shared `/allowlist` plumbing.
- This weakens the repo's documented control-plane privilege split between ordinary write actions and admin-only persistent authorization mutation.

## Remediation

### 1) Add the Missing Sink-Side Internal Admin Check to `/allowlist`

Mirror the existing hardened pattern from `/config` and `/plugins`.

Before any config-backed `/allowlist add|remove` write, require:

- `operator.admin` for internal gateway channels

This should happen before `plugin.allowlist.applyConfigEdit(...)` and before `writeConfigFile(...)`.

### 2) Keep Pairing-Store and Config-Write Policy Checks, but Do Not Treat Them as Scope Enforcement

`configWrites` policy and pairing-store behavior are useful secondary controls, but they do not replace the missing privilege check between `operator.write` and `operator.admin`.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-94pw-c6m8-p9p9
- https://github.com/openclaw/openclaw
