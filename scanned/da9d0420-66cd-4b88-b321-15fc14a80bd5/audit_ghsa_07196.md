# [H] New API: SSRF Protection Bypass via Unresolved Hostname in Notification URLs

## Summary
Severity: High
Advisory: GHSA-6qcr-qxgr-m7fv
CVE: CVE-2026-33655
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-07
Source: https://github.com/advisories/GHSA-6qcr-qxgr-m7fv
Type: github-advisory

## Affected
- Go: `github.com/QuantumNous/new-api` — affected >=0 <0.12.0-alpha.1

## Details
## Summary

The default SSRF protection configuration did not apply IP filtering to hostnames. With `ApplyIPFilterForDomain` disabled by default, URL validation checked domain allow/block rules but did not resolve a hostname and validate the resolved IP address. Authenticated users could configure notification URLs for Webhook, Bark, or Gotify notifications and point a hostname at an internal or metadata IP address.

## Impact

A regular authenticated user could cause the server to send notification requests to internal HTTP services reachable from the deployment network. Depending on the target environment, this could expose sensitive internal data through timing, errors, or response-dependent behavior. The issue is rated High.

## Affected versions

Versions before `v0.12.0-alpha.1` are affected. The previous affected range of `<= v0.11.4-alpha.4` was too narrow because the unsafe default remained present until the `v0.12.0-alpha.1` fix.

## Patches

This issue is fixed in `v0.12.0-alpha.1`. The default fetch setting now sets `ApplyIPFilterForDomain: true`, causing hostname destinations to be resolved and checked against the configured IP filtering rules during URL validation.

This patch addresses the unresolved-hostname bypass for the affected notification URL paths. It does not mark the separate DNS rebinding advisory as fixed, because connection-time IP enforcement is tracked separately.

## Workarounds

If upgrading immediately is not possible, explicitly enable `ApplyIPFilterForDomain`, restrict notification URL domains with an allowlist, disable user-configurable notification URLs where practical, and enforce outbound network filtering at the host or network layer.

## Resources

- Fixed by commit `20399d3c8fcb4e3649d53163eb11940fd6763743`.
- Relevant code paths: `setting/system_setting/fetch_setting.go`, `common/ssrf_protection.go`, `service/webhook.go`, and `service/user_notify.go`.

## References
- https://github.com/QuantumNous/new-api/security/advisories/GHSA-6qcr-qxgr-m7fv
- https://github.com/QuantumNous/new-api/commit/20399d3c8fcb4e3649d53163eb11940fd6763743
- https://github.com/QuantumNous/new-api
