# [C] Appsmith public apps can execute unpublished actions (viewMode confusion)

## Summary
Severity: Critical
Advisory: BIT-appsmith-2026-24042
Aliases: CVE-2026-24042, GHSA-j9qq-4fj9-9883
Ecosystem: Bitnami
Published: 2026-01-29
Source: https://osv.dev/vulnerability/BIT-appsmith-2026-24042
Type: osv

## Affected
- Bitnami: `appsmith` — affected >=0 <1.95.0

## Details
Appsmith is a platform to build admin panels, internal tools, and dashboards. In versions 1.94 and below, publicly accessible apps allow unauthenticated users to execute unpublished (edit-mode) actions by sending viewMode=false (or omitting it) to POST /api/v1/actions/execute. This bypasses the expected publish boundary where public viewers should only execute published actions, not edit-mode versions. An attack can result in sensitive data exposure, execution of edit‑mode queries and APIs, development data access, and the ability to trigger side effect behavior. This issue does not have a released fix at the time of publication.

## References
- https://github.com/appsmithorg/appsmith/security/advisories/GHSA-j9qq-4fj9-9883
- https://nvd.nist.gov/vuln/detail/CVE-2026-24042
