# [H] UltraDAG: Smart Account Spending Policy Bypass via Pockets

## Summary
Severity: High
Advisory: CVE-2026-42278
Aliases: GHSA-9chc-gjfr-6hrq
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-42278
Type: osv

## Details
UltraDAG is a minimal DAG-BFT blockchain in Rust. Prior to commit fb6ef59, the UltraDAG StateEngine implementation of SmartTransferTx contains a critical logic flaw in its policy enforcement pipeline. When a transaction originates from a "Pocket" (a derived sub-address documented in the protocol as a way to organize funds), the engine fails to resolve the pocket's parent account before checking the spending policy. Because pockets are "virtual" addresses that exist only as entries in the pocket_to_parent map and do not have their own SmartAccountConfig entries, the check_spending_policy method defaults to an "authorized/no policy" result. This allow any user (or attacker in possession of a parent key) to instantly drain every pocket on an account, even if the parent account has a strict 24-hour vault delay or a 1 UDAG daily limit. This issue has been patched via commit fb6ef59.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42278.json
- https://github.com/UltraDAGcom/core/security/advisories/GHSA-9chc-gjfr-6hrq
- https://nvd.nist.gov/vuln/detail/CVE-2026-42278
- https://github.com/UltraDAGcom/core/commit/fb6ef59d6c1385400e7acea7ae31fc6a473c3051
