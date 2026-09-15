# [H] Nebula Mesh: Web UI lacks ownership checks, enabling cross-operator access to hosts and networks (read, block, delete)

## Summary
Severity: High
Advisory: GHSA-c6v2-3ffm-vcmc
CVE: CVE-2026-49258
CWE: CWE-639, CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-c6v2-3ffm-vcmc
Type: github-advisory

## Affected
- Go: `github.com/juev/nebula-mesh` — affected >=0

## Details
## Summary

The web UI (`/ui/*`) does not apply the per-operator CA scoping the JSON API received for GHSA-598g-h2vc-h5vg. Any authenticated non-admin operator (for example, one created via self-registration or OIDC) can access resources belonging to other operators.

## Impact

A non-admin operator can:

- **Block or delete any other operator's host.** `POST /ui/hosts/{id}/block` and `DELETE /ui/hosts/{id}` act on the URL `id` with no ownership check, so a non-admin can block (revoking the host's certificate via the blocklist) or delete any host in the deployment — a cross-operator denial of service.
- **Read every operator's hosts and networks.** The dashboard, `/ui/hosts`, the host detail page, `/ui/networks` (including the create-form error re-render), and the `/ui/events` stream all return data across all operators, exposing host names, Nebula IPs, public IPs, certificate fingerprints and expiry, and network names and CIDRs.

This is the same cross-operator class as GHSA-598g; that remediation covered the JSON API but not the web read/mutation surface. The host create/edit/mobile-bundle/network-create paths and all CA-management routes were already correctly scoped.

Affected handlers (`internal/web`): `handleHostDetail`, `handleHostBlock`, `handleHostDelete`, `handleDashboard`, `handlePartialStats`, `handleHosts`, `handleNetworks`, `renderNetworksError`, `handleHostEvents`.

## Conditions

Exposure requires at least one non-admin operator to exist (self-registration enabled, OIDC, or an admin-created user). A single-admin deployment with no additional operators is not affected.

## Fix

A complete candidate fix with regression tests is ready in a private repository shared with the maintainer (`ak2k/nebula-mesh-ghsa-web`, PR #1): scope these handlers to the session operator's owned CAs (admins keep the full view), mirroring the API's ownership checks.

## References
- https://github.com/juev/nebula-mesh/security/advisories/GHSA-c6v2-3ffm-vcmc
- https://github.com/juev/nebula-mesh
