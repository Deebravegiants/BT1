# [H] ClearanceKit: opfilter policy bypass via non-open file operations

## Summary
Severity: High
Advisory: CVE-2026-33631
Aliases: GHSA-25f8-8cj2-m887
CVSS: 8.7 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L)
Published: 2026-03-26
Source: https://osv.dev/vulnerability/CVE-2026-33631
Type: osv

## Details
ClearanceKit intercepts file-system access events on macOS and enforces per-process access policies. In versions on the 4.1 branch and earlier, the opfilter Endpoint Security system extension enforced file access policy exclusively by intercepting ES_EVENT_TYPE_AUTH_OPEN events. Seven additional file operation event types were not intercepted, allowing any locally running process to bypass the configured FAA policy without triggering a denial. Commit a3d1733 adds subscriptions for all seven event types and routes them through the existing FAA policy evaluator. AUTH_RENAME and AUTH_UNLINK additionally preserve XProtect change detection: events on the XProtect path are allowed and trigger the existing onXProtectChanged callback rather than being evaluated against user policy. All versions on the 4.2 branch contain the fix. No known workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33631.json
- https://github.com/craigjbass/clearancekit/security/advisories/GHSA-25f8-8cj2-m887
- https://nvd.nist.gov/vuln/detail/CVE-2026-33631
- https://github.com/craigjbass/clearancekit/commit/a3d1733d2691a0d40209c48b01bf9291bf645207
