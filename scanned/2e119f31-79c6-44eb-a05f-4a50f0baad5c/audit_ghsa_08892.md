# [M] Default kuma-cp leaks admin token cross-origin via CORS wildcard + LocalhostIsAdmin

## Summary
Severity: Medium
Advisory: GHSA-3vcp-chfh-f6r2
CVE: CVE-2026-45021
CWE: CWE-346, CWE-942
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-3vcp-chfh-f6r2
Type: github-advisory

## Affected
- Go: `github.com/kumahq/kuma` — affected >=0 <2.7.25
- Go: `github.com/kumahq/kuma` — affected >=2.9.0 <2.9.15
- Go: `github.com/kumahq/kuma` — affected >=2.11.0 <2.11.13
- Go: `github.com/kumahq/kuma` — affected >=2.12.0 <2.12.10
- Go: `github.com/kumahq/kuma` — affected >=2.13.0 <2.13.5

## Details
## Summary

Default `kuma-cp` config leaks the admin bootstrap token and signing keys to any webpage the operator visits while the control plane is reachable from their browser. `CorsAllowedDomains: [".*"]` reflects any `Origin`, and `LocalhostIsAdmin: true` promotes requests from `127.0.0.1` to `mesh-system:admin`. A cross-origin `fetch()` from a malicious page returns the admin JWT and signing material.

## Am I affected?

You are affected if all of these hold:

1. `kuma-cp` runs with default config (`CorsAllowedDomains: [".*"]` and `LocalhostIsAdmin: true`).
2. The control plane is reachable from a browser on the same machine:
   - `kuma-cp run` on a developer laptop
   - Docker `--network host` or port-publish on a workstation
   - `kubectl port-forward` from a machine that also browses the web
3. The operator visits a page running attacker JavaScript while the control plane is reachable.

You are not affected if:

- The control plane runs on a Kubernetes cluster accessed via ClusterIP, NodePort, or LoadBalancer from a remote client.
- The control plane runs on an SSH-administered VM with no browser on the host.
- `KUMA_API_SERVER_AUTHN_LOCALHOST_IS_ADMIN=false` is set (see https://kuma.io/docs/latest/production/secure-deployment/api-server-auth/).
- `KUMA_API_SERVER_CORS_ALLOWED_DOMAINS` is set to an explicit allowlist that excludes attacker origins.

## Mitigation

1. Set `KUMA_API_SERVER_AUTHN_LOCALHOST_IS_ADMIN=false` after retrieving the admin token.
2. Set `KUMA_API_SERVER_CORS_ALLOWED_DOMAINS` to an explicit allowlist, for example `http://localhost:5681,http://127.0.0.1:5681`.
3. Do not run `kuma-cp` on a machine where you browse untrusted sites.

## Fix

Fixed in [#16416](https://github.com/kumahq/kuma/pull/16416), backported to all supported release branches ([#16423](https://github.com/kumahq/kuma/pull/16423), [#16424](https://github.com/kumahq/kuma/pull/16424), [#16425](https://github.com/kumahq/kuma/pull/16425), [#16426](https://github.com/kumahq/kuma/pull/16426), [#16427](https://github.com/kumahq/kuma/pull/16427)).

Changes in patched versions:

- `CorsAllowedDomains` default changed from `[".*"]` to `[]` — CORS is now opt-in; set the env var explicitly if you need GUI access.
- `LocalhostIsAdmin` hardened: now requires direct loopback `RemoteAddr` and `Host`, and rejects requests carrying proxy-hop headers (`X-Forwarded-For`), cross-site fetch metadata (`Sec-Fetch-Site`), or a non-localhost `Origin`.

Upgrade to a patched version:

- 2.7.25
- 2.9.15
- 2.11.13
- 2.12.10
- 2.13.5

## Credits

Reported by `eldudareeno`.

## CVSS

`CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N` = 5.1 Medium.

## References
- https://github.com/kumahq/kuma/security/advisories/GHSA-3vcp-chfh-f6r2
- https://nvd.nist.gov/vuln/detail/CVE-2026-45021
- https://github.com/kumahq/kuma/pull/16416
- https://github.com/kumahq/kuma/pull/16423
- https://github.com/kumahq/kuma/pull/16424
- https://github.com/kumahq/kuma/pull/16425
- https://github.com/kumahq/kuma/pull/16426
- https://github.com/kumahq/kuma/pull/16427
- https://github.com/kumahq/kuma/commit/8fefa8595d44eb68d922405702ed7a0826322907
- https://github.com/kumahq/kuma
