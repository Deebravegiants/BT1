# [H] Unbounded max_fee_per_gas in mpp Tempo fee-payer enables single-request wallet drain

## Summary
Severity: High
Advisory: CVE-2026-59695
Aliases: EEF-CVE-2026-59695, GHSA-vv77-66rf-pm86
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-17
Source: https://osv.dev/vulnerability/CVE-2026-59695
Type: osv

## Details
Improper Validation of Specified Quantity in Input in ZenHive mpp allows an unauthenticated remote client to drain the fee-payer wallet in a single request by naming an arbitrarily high gas price.

When the mpp Elixir library is configured as fee payer (fee_payer: true), MPP.Tempo.Transaction.cosign_fee_payer/3 re-signs the client-supplied base fields of the 0x76 AASigned envelope verbatim, including max_fee_per_gas and max_priority_fee_per_gas, without validating that they are within reasonable bounds. A malicious client embeds arbitrarily large values for these fields in the signed envelope. The server co-signs and broadcasts the transaction. The effective_gas_price billed against the fee-payer wallet is derived from the attacker-supplied ceilings, so the server pays those inflated per-gas rates out of its own wallet. A single crafted request can drain the wallet entirely, after which the server can no longer sponsor gas for legitimate payment requests.

This issue affects mpp: from 0.2.0 before 0.6.0.

## References
- https://cna.erlef.org/cves/CVE-2026-59695.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-59695
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59695.json
- https://github.com/ZenHive/mpp/security/advisories/GHSA-vv77-66rf-pm86
- https://nvd.nist.gov/vuln/detail/CVE-2026-59695
- https://github.com/ZenHive/mpp/commit/5d6338e2334084c5f2a78cfcca474830733ed7e8
- https://github.com/ZenHive/mpp
