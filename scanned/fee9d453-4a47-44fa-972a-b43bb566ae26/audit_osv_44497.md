# [M] Unbounded key authorization in mpp Tempo fee-payer sponsorship inflates gas cost and sponsors access-key provisioning

## Summary
Severity: Medium
Advisory: CVE-2026-82751
Aliases: EEF-CVE-2026-82751, GHSA-rpwj-vrf7-4x36
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-09-06
Source: https://osv.dev/vulnerability/CVE-2026-82751
Type: osv

## Details
Improper Validation of Specified Quantity in Input in ZenHive mpp allows an unauthenticated remote client to inflate the fee-payer's gas cost per sponsored payment by a large multiplier and to have the sponsor pay for provisioning an access key on the client's own account.

When the server sponsors Tempo payments, MPP.Methods.Tempo.FeePayerPolicy.measure/3 in lib/mpp/methods/tempo/fee_payer_policy.ex bounds the gas fields, the fee budget, the validity window and the access list of the client-signed 0x76 envelope, but does not check whether the envelope carries the optional key_authorization field. A client can attach a fully signed key authorization, provisioning a new access key with token spending limits on its own account, alongside the normal payment call. The key and each limit entry are persistent storage writes billed as intrinsic gas to the sponsor, bounded only by the gas_limit ceiling. At the reporter's default of one key with three token limits the sponsored cost rises from about 46,587 gas to about 1,808,700 gas, and the client keeps a valid access key it paid nothing for.

This issue affects mpp: from 0.2.0 before 0.16.1.

## References
- https://cna.erlef.org/cves/CVE-2026-82751.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-82751
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82751.json
- https://github.com/ZenHive/mpp/security/advisories/GHSA-rpwj-vrf7-4x36
- https://nvd.nist.gov/vuln/detail/CVE-2026-82751
- https://github.com/ZenHive/mpp/commit/0482572b47e1ffe1537ab80ab613d47b92833c2d
- https://github.com/ZenHive/mpp
