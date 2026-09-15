# [H] Clauster: Non-loopback deployments can serve the dashboard unauthenticated when auth.enabled is unset

## Summary
Severity: High
Advisory: GHSA-h4g2-xfmw-q2c9
CWE: CWE-306
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:A/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-10
Source: https://github.com/advisories/GHSA-h4g2-xfmw-q2c9
Type: github-advisory

## Affected
- PyPI: `clauster` — affected >=0 <0.2.2

## Details
### Summary
A Clauster instance bound to a **non-loopback** address (e.g. `0.0.0.0` or a LAN IP) can serve the entire dashboard and its API **without any authentication** — even when the operator has configured a password — if `auth.enabled` is left at its default (`false`). The operator believes the instance is password-protected; in reality every request is served unauthenticated.

### Impact
An unauthenticated attacker with network access to the instance gains full control of the dashboard: list projects, **spawn/stop `claude remote-control` bridges in any project directory**, edit `CLAUDE.md`, read bridge logs, and (where configured) clone repositories. Because bridges run Claude Code against the host's project directories, this is effectively remote code execution in those projects.

Loopback (`127.0.0.1`) deployments need no auth by design and are **not** affected.

### Affected configurations
All released versions (≤ 0.2.1) where **all** of the following hold:
- `host` is a non-loopback address, **and**
- `auth.password_required: true` and/or `auth.reverse_proxy.enabled: true` is set, **and**
- `auth.enabled` is left at its default `false`.

Docker deployments are affected: the image binds `0.0.0.0`, and the previously-documented `docker run` command did not set `auth.enabled`.

### Root cause
Two layers checked different flags:
- The runtime auth guard enforces authentication only when `config.auth.enabled` is true; when false it passes **every** request through unauthenticated.
- The config validator, for a non-loopback bind, required only one of `auth.password_required` / `auth.reverse_proxy.enabled` / `auth.allow_unauthenticated_network` — **not** `auth.enabled`. So a config with a password but `enabled=false` validated, started, and enforced nothing.

### Proof of concept
With `host: 0.0.0.0`, `auth.password_required: true`, a valid `auth.password_hash`, and `auth.enabled` unset:

```
curl http://<host>:7621/api/instances
```

returns `200` with the full instance list and **no credentials**. Setting `auth.enabled: true` returns `401`.

### Patches
An upcoming patch release makes the config validator **fail closed**: a non-loopback bind is refused unless authentication is actually enforced — `auth.enabled: true` together with `auth.password_required` (+ a hash) or `auth.reverse_proxy.enabled`, or the explicit `auth.allow_unauthenticated_network` opt-out. The README, `clauster.yml.example`, and Docker docs were corrected to match.

### Workaround
On any non-loopback deployment, set `auth.enabled: true` in `clauster.yml` (or `CLAUSTER_AUTH_ENABLED=true`) alongside your existing `auth.password_required` + hash (or reverse-proxy) settings. Alternatively, bind to loopback only and reach it via an SSH tunnel or a trusted authenticating reverse proxy.

### Credit
Found during an internal security review.

## References
- https://github.com/schubydoo/clauster/security/advisories/GHSA-h4g2-xfmw-q2c9
- https://github.com/schubydoo/clauster
