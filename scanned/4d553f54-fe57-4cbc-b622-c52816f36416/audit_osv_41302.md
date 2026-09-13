# [M] Missing gas_limit validation in mpp Tempo fee-payer enables wallet drain

## Summary
Severity: Medium
Advisory: CVE-2026-59252
Aliases: EEF-CVE-2026-59252, GHSA-vj8p-hp9x-gh47
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-17
Source: https://osv.dev/vulnerability/CVE-2026-59252
Type: osv

## Details
Improper Validation of Specified Quantity in Input in ZenHive mpp allows an unauthenticated remote client to drain the fee-payer wallet, resulting in denial of service for legitimate clients.

When the mpp Elixir library is configured as fee payer (fee_payer: true), the MPP.Methods.Tempo payment method co-signs and broadcasts a client-supplied EVM transaction without first validating that the client-supplied gas_limit is sufficient to complete the intended call. A malicious client can submit a signed transferWithMemo transaction with gas_limit deliberately set just below the amount required for successful execution. The server co-signs the transaction and broadcasts it via rpc_broadcast_sync. The transaction runs out of gas during EVM execution and reverts, but the fee-payer wallet is still charged for the burned gas while the client pays nothing and receives no resource. Repeated requests from one or more malicious clients drain the fee-payer wallet at near-zero cost to the attacker, ultimately preventing the server from sponsoring gas for legitimate payment requests.

The wait_for_confirmation = false (optimistic) path is also affected: it invokes simulate_payment_call via eth_call, but that simulation omits the gas parameter and therefore does not catch out-of-gas conditions.

This issue affects mpp: from 0.2.0 before 0.6.0.

## References
- https://cna.erlef.org/cves/CVE-2026-59252.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-59252
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59252.json
- https://github.com/ZenHive/mpp/security/advisories/GHSA-vj8p-hp9x-gh47
- https://nvd.nist.gov/vuln/detail/CVE-2026-59252
- https://github.com/ZenHive/mpp/commit/d84e3e528db39654540c2035ea0fbdf7b950d3d1
- https://github.com/ZenHive/mpp
