# [M] Daytona: Cross-tenant data leak in notification WebSocket gateway via unverified organizationId join

## Summary
Severity: Medium
Advisory: GHSA-qwxf-2m7m-2m3x
CVE: CVE-2026-54324
CWE: CWE-639, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-qwxf-2m7m-2m3x
Type: github-advisory

## Affected
- Go: `github.com/daytonaio/daytona` — affected >=0 <0.185.0

## Details
### Summary
A cross-tenant authorization flaw in Daytona's notification WebSocket gateway allowed any authenticated user to subscribe to another organization's realtime notification channel and passively receive that organization's events.

### Impact
The notification gateway's JWT handshake joined a client-supplied organization identifier to the corresponding notification room without verifying that the authenticated user was a member of that organization. As a result, an authenticated user could receive another organization's realtime sandbox, snapshot, volume, and runner events, including data carried in those events. This is a cross-tenant confidentiality break. It required a valid account and knowledge of the target organization id (a non-secret UUID); no elevated privileges were needed. The API-key authentication path was not affected.

The affected component is the Daytona API service (the `apps/api` NestJS application). It is distributed through Daytona's repository releases and container images for self-hosted deployments; it is not published as a Go or npm package, so the advisory will not surface through `go get` or npm dependency tooling.

### Affected Versions
>= 0.101.0, <= 0.184.0

### Patched Versions
0.185.0

### Credit
@vnth4nhnt from CyStack

## References
- https://github.com/daytonaio/daytona/security/advisories/GHSA-qwxf-2m7m-2m3x
- https://nvd.nist.gov/vuln/detail/CVE-2026-54324
- https://github.com/daytonaio/daytona
