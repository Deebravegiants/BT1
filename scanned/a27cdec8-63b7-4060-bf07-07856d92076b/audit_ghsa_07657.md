# [H] OpenClaw vulnerable to Unauthenticated Local RCE via WebSocket config.apply

## Summary
Severity: High
Advisory: GHSA-g55j-c2v4-pjcg
CVE: CVE-2026-25593
CWE: CWE-20, CWE-306, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-04
Source: https://github.com/advisories/GHSA-g55j-c2v4-pjcg
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.1.20

## Details
### Summary

An unauthenticated local client could use the Gateway WebSocket API to write config via `config.apply` and set unsafe `cliPath` values that were later used for command discovery, enabling command injection as the gateway user.

### Impact

A local process on the same machine could execute arbitrary commands as the gateway process user.

### Details

- `config.apply` accepted raw JSON and wrote it to disk after schema validation.
- `cliPath` values were not constrained to safe executable names/paths.
- Command discovery used a shell invocation when resolving executables.

### Mitigation

Upgrade to a patched release. If projects cannot upgrade immediately, set `gateway.auth` and avoid custom `cliPath` values.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-g55j-c2v4-pjcg
- https://nvd.nist.gov/vuln/detail/CVE-2026-25593
- https://github.com/openclaw/openclaw
