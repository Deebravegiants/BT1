# [M] AshAi aggregate tool can read field-policy-protected fields

## Summary
Severity: Medium
Advisory: CVE-2026-78230
Aliases: EEF-CVE-2026-78230, GHSA-v5rw-36x5-r5vx
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-08
Source: https://osv.dev/vulnerability/CVE-2026-78230
Type: osv

## Details
AshAi exposes Ash read actions to language-model tool calls. The read tool accepts an aggregate result type (min, max, sum, avg) that builds an ad-hoc Ash.Query.Aggregate over a named field and returns its raw value.

Ash field policies redact forbidden fields on returned records (replacing them with %Ash.ForbiddenField{}), but that redaction does not apply to aggregate values. A tool caller could therefore read a field the calling actor's field policies forbid by requesting it as an aggregate; min/max in particular return an actual field value. This includes fields that are public? true but restricted per-actor by a field policy, such as sensitive PII. The tool's existing check only required the field to be public, which is a separate axis from per-actor field-policy authorization.

The fix authorizes the aggregated field against the resource's field policies, so aggregating over a field the actor may not see is refused or scoped to the rows where it is visible.

This issue affects ash_ai: from 0.1.0 before 1.0.3.

## References
- https://cna.erlef.org/cves/CVE-2026-78230.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-78230
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/78xxx/CVE-2026-78230.json
- https://github.com/ash-project/ash_ai/security/advisories/GHSA-v5rw-36x5-r5vx
- https://nvd.nist.gov/vuln/detail/CVE-2026-78230
- https://github.com/ash-project/ash_ai/commit/2ba234b50946a3b8116190c8467f9f4dfa5edce7
- https://github.com/ash-project/ash_ai/commit/9c02de581625c342c9870a672830bff28c1d701e
- https://github.com/ash-project/ash_ai
