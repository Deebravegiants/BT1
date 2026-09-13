# [M] OpenClaw has a sandbox network isolation bypass via docker.network=container:<id>

## Summary
Severity: Medium
Advisory: GHSA-ww6v-v748-x7g9
CVE: CVE-2026-32038
CWE: CWE-284, CWE-693
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-ww6v-v748-x7g9
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.24

## Details
### Summary
In `openclaw@2026.2.23`, sandbox network hardening blocks `network=host` but still allows `network=container:<id>`.

This can let a sandbox join another container's network namespace and reach services available in that namespace.

### Preconditions and Trust Model Context
This issue requires a trusted-operator configuration path (for example setting `agents.defaults.sandbox.docker.network` in gateway config). It is not an unauthenticated remote exploit by itself.

### Details
Current validation blocks only `host`, while forwarding other values to Docker create args:

- `validateNetworkMode(network)` only rejects values in `BLOCKED_NETWORK_MODES = {"host"}`.
- `buildSandboxCreateArgs(...)` validates then forwards `cfg.network` into `--network`.
- Browser sandbox helper also treats `container:` as an accepted mode in network preparation.

Effective behavior:

- `host` -> blocked
- `container:<id>` -> accepted and forwarded

### Impact
Type: sandbox network isolation hardening bypass.

Practical impact depends on deployment:

- Requires ability to influence trusted sandbox network config.
- Higher impact when a target container exposes privileged/internal network reachability.

### Remediation
Block namespace-join style network modes (including `container:<id>`) for sandbox containers, and keep strict allowlisting for safe network modes.


### Patch Status
Fixed on `main` in commit `14b6eea6e`:
https://github.com/openclaw/openclaw/commit/14b6eea6e

Follow-up refactor/cleanup (no policy rollback):
https://github.com/openclaw/openclaw/commit/5552f9073


### Publication Update (2026-02-25)
`openclaw@2026.2.24` is published on npm and contains the fix commit(s) listed above. This advisory now marks `>= 2026.2.24` as patched.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-ww6v-v748-x7g9
- https://nvd.nist.gov/vuln/detail/CVE-2026-32038
- https://github.com/openclaw/openclaw/commit/14b6eea6e
- https://github.com/openclaw/openclaw/commit/5552f9073
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-sandbox-network-isolation-bypass-via-docker-network-container-parameter
