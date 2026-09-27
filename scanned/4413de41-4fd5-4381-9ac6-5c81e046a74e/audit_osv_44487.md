# [M] Authorization-redacted field values disclosed through AshTypescript result normalization

## Summary
Severity: Medium
Advisory: CVE-2026-82730
Aliases: EEF-CVE-2026-82730, GHSA-6929-rjmh-4x62
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-82730
Type: osv

## Details
Incorrect Authorization vulnerability in ash-project ash_typescript allows an unauthorized RPC caller to read attribute values that Ash field policies denied.

When a field policy denies an attribute, Ash substitutes %Ash.ForbiddenField{}, which retains the real value in original_value because embedded resources must remain writable, and hides it from Inspect rather than removing it. AshTypescript.Rpc.ResultProcessor strips these markers to nil on its template-driven paths, but normalize_primitive/1 in lib/ash_typescript/rpc/result_processor.ex had no such clause, so a marker fell through to the generic struct branch which calls Map.from_struct/1 and serializes every key, original_value included. The denied value is returned to the caller inside the marker that represents its own denial.

The simplest trigger is an action returning an embedded resource as a map, which routes through normalize_resource_struct/2 with an empty template. normalize_value_for_json/1 is a public, unguarded entry point to the same path.

This issue affects ash_typescript: from 0.11.0 before 0.18.0.

## References
- https://cna.erlef.org/cves/CVE-2026-82730.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-82730
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82730.json
- https://github.com/ash-project/ash_typescript/security/advisories/GHSA-6929-rjmh-4x62
- https://nvd.nist.gov/vuln/detail/CVE-2026-82730
- https://github.com/ash-project/ash_typescript/commit/aa7f9f1967b0bec806ac1156142267e805d70a55
- https://github.com/ash-project/ash_typescript
