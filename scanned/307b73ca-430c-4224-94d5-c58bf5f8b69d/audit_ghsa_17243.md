# [M] Temporal has an Incorrect Authorization vulnerability

## Summary
Severity: Medium
Advisory: GHSA-hmhp-gh8m-c8xp
CVE: CVE-2025-14987
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:L/VA:L/SC:L/SI:L/SA:L (CVSS_V4)
Published: 2025-12-30
Source: https://github.com/advisories/GHSA-hmhp-gh8m-c8xp
Type: github-advisory

## Affected
- Go: `go.temporal.io/server` — affected >=0 <1.27.4
- Go: `go.temporal.io/server` — affected >=1.28.0 <1.28.2
- Go: `go.temporal.io/server` — affected >=1.29.0 <1.29.2
- Go: `go.temporal.io/server` — affected >=1.29.0-0 <1.29.0-135.0.0.20251218190115-b292a32bacdf

## Details
When system.enableCrossNamespaceCommands is enabled (on by default), the Temporal server permits certain workflow task commands (e.g. StartChildWorkflowExecution, SignalExternalWorkflowExecution, RequestCancelExternalWorkflowExecution) to target a different namespace than the namespace authorized at the gRPC boundary. The frontend authorizes RespondWorkflowTaskCompleted based on the outer request namespace, but the history service later resolves and executes the command using the namespace embedded in command attributes without authorizing the caller for that target namespace. This can allow a worker authorized for one namespace to create, signal, or cancel workflows in another namespace.
This issue affects Temporal: through 1.29.1. Fixed in 1.27.4, 1.28.2, 1.29.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-14987
- https://github.com/temporalio/temporal/commit/b292a32bacdfa6472affd90f0a940408d5839cfa
- https://github.com/temporalio/temporal
- https://github.com/temporalio/temporal/releases/tag/v1.27.4
- https://github.com/temporalio/temporal/releases/tag/v1.28.2
- https://github.com/temporalio/temporal/releases/tag/v1.29.2
