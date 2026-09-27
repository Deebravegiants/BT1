# [M] UltraDAG: SmartOp Vote Path Triggers Fatal Supply Invariant Halt

## Summary
Severity: Medium
Advisory: CVE-2026-40583
Aliases: GHSA-q8wx-2crx-c7pp
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N/U:Red)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/CVE-2026-40583
Type: osv

## Details
UltraDAG is a minimal DAG-BFT blockchain in Rust. In version 0.1, a non-council attacker can submit a signed SmartOp::Vote transaction that passes signature, nonce, and balance prechecks, but fails authorization only after state mutation has already occurred.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40583.json
- https://github.com/UltraDAGcom/core/security/advisories/GHSA-q8wx-2crx-c7pp
- https://nvd.nist.gov/vuln/detail/CVE-2026-40583
- https://github.com/UltraDAGcom/core/commit/2f5a3a237ea519b48d71e6e3093c89f60694c7be
- https://github.com/UltraDAGcom/core/commit/45bcf7064741897319b6196d3d9f9e1307093511
