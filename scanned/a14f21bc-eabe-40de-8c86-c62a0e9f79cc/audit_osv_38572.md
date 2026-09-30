# [H] ClearanceKit: Ad-hoc signed binaries can spoof Apple process identities in the global allowlist

## Summary
Severity: High
Advisory: CVE-2026-40599
Aliases: GHSA-w253-42qp-5f2x
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/CVE-2026-40599
Type: osv

## Details
ClearanceKit intercepts file-system access events on macOS and enforces per-process access policies. Prior to 5.0.5, ClearanceKit incorrectly treats a process with an empty Team ID and a non-empty Signing ID as an Apple platform binary. This bug allows a malicious software to impersonate an apple process in the global allowlist, and access all protected files. This vulnerability is fixed in 5.0.5.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40599.json
- https://github.com/craigjbass/clearancekit/security/advisories/GHSA-w253-42qp-5f2x
- https://nvd.nist.gov/vuln/detail/CVE-2026-40599
