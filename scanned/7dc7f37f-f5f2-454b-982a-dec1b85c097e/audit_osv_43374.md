# [H] Tempo fee sponsorship in mpp bounds each transaction but not aggregate exposure, allowing concurrent sponsor-wallet drain

## Summary
Severity: High
Advisory: CVE-2026-73541
Aliases: EEF-CVE-2026-73541, GHSA-j4j7-7xpr-c7cr
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-73541
Type: osv

## Details
Allocation of Resources Without Limits or Throttling in ZenHive mpp allows an unauthenticated remote client to drain the fee-payer wallet through concurrent sponsored payments, denying service to legitimate payers once it is empty.

MPP.Methods.Tempo.FeePayerPolicy enforces its ceilings (max_gas, max_fee_per_gas, max_priority_fee_per_gas, the worst-case gas_limit * max_fee_per_gas <= max_total_fee budget cap, and a validity window) against one transaction at a time, and nothing accounts for exposure across concurrent requests. reserve_hash_atomic/2 is keyed on the transaction hash, so it prevents duplicate broadcast of the same signed transaction but not N distinct sponsored transactions carrying distinct expiring nonces. Committed sponsor exposure is therefore N times max_total_fee, bounded by nothing in the library, and the default 900 second validity window lets co-signed transactions stay broadcastable and uncounted for that entire period.

This issue affects mpp: from 0.2.0 before 0.12.0.

## References
- https://cna.erlef.org/cves/CVE-2026-73541.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-73541
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73541.json
- https://github.com/ZenHive/mpp/security/advisories/GHSA-j4j7-7xpr-c7cr
- https://nvd.nist.gov/vuln/detail/CVE-2026-73541
- https://github.com/ZenHive/mpp/commit/ddc46868fba57ccebb567c04709812b466123076
- https://github.com/ZenHive/mpp
