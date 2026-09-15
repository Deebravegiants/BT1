# [M] AshLua eval read operations can read field-policy-protected fields via aggregates

## Summary
Severity: Medium
Advisory: CVE-2026-78216
Aliases: EEF-CVE-2026-78216, GHSA-5whv-8rcp-x33j
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-08
Source: https://osv.dev/vulnerability/CVE-2026-78216
Type: osv

## Details
AshLua exposes Ash read actions to Lua scripts run through an eval action. A read call accepts an operation (list, min, max, first, sum, avg) that builds an ad-hoc Ash.Query.Aggregate over a named field and returns its raw value.

Ash field policies redact forbidden fields on returned records (replacing them with %Ash.ForbiddenField{}), but that redaction does not apply to aggregate values. A script could therefore read a field the calling actor's field policies forbid by requesting it as an aggregate instead of as a field. This includes fields that are public? true but restricted per-actor by a field policy, such as sensitive PII. The prior hardening only enforced the exposed-field allow-list (field visibility), which is a separate axis from per-actor field-policy authorization.

The fix authorizes the aggregated field against the resource's field policies, so aggregating over a field the actor may not see is refused or scoped to the rows where it is visible.

This issue affects ash_lua: from 0.1.0 before 0.2.2.

## References
- https://cna.erlef.org/cves/CVE-2026-78216.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-78216
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/78xxx/CVE-2026-78216.json
- https://github.com/ash-project/ash_lua/security/advisories/GHSA-5whv-8rcp-x33j
- https://nvd.nist.gov/vuln/detail/CVE-2026-78216
- https://github.com/ash-project/ash_lua/commit/266a5dcc56d5015b6d316c10606169e753b07450
- https://github.com/ash-project/ash_lua/commit/8675e47cca81f36594083a7e63379bac9e123e72
- https://github.com/ash-project/ash_lua
