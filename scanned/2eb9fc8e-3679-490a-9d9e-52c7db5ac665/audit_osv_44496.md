# [M] Unbounded EIP-7702 authorization list in mpp Tempo fee-payer sponsorship inflates gas cost and sponsors account delegation

## Summary
Severity: Medium
Advisory: CVE-2026-82750
Aliases: EEF-CVE-2026-82750, GHSA-5qrp-r24c-w6jr
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-09-06
Source: https://osv.dev/vulnerability/CVE-2026-82750
Type: osv

## Details
Improper Validation of Specified Quantity in Input in ZenHive mpp allows an unauthenticated remote client to inflate the fee-payer's gas cost per sponsored payment by a large multiplier and to have the sponsor pay for EIP-7702 account delegations of the client's choosing.

When the server sponsors Tempo payments, MPP.Methods.Tempo.FeePayerPolicy.measure/3 in lib/mpp/methods/tempo/fee_payer_policy.ex bounds the gas fields, the fee budget, the validity window and the access list of the client-signed 0x76 envelope, but never reads its aa_authorization_list field. Every signed delegation in that list is charged as intrinsic gas before the payment call runs, so a client attaching delegations from throwaway authority keys makes the sponsor pay for them within the default gas_limit ceiling. At the reporter's default of seven entries the sponsored cost rises from about 46,575 gas to about 1,884,087 gas. Because each entry is applied as a persistent set-code delegation, a client can also upgrade its own accounts to delegated code at the sponsor's expense.

This issue affects mpp: from 0.2.0 before 0.16.1.

## References
- https://cna.erlef.org/cves/CVE-2026-82750.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-82750
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82750.json
- https://github.com/ZenHive/mpp/security/advisories/GHSA-5qrp-r24c-w6jr
- https://nvd.nist.gov/vuln/detail/CVE-2026-82750
- https://github.com/ZenHive/mpp/commit/0482572b47e1ffe1537ab80ab613d47b92833c2d
- https://github.com/ZenHive/mpp
