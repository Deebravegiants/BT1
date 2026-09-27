# [H] Signum Node: Integer overflow in SMART_FEES fee distribution allows arbitrary miner reward inflation

## Summary
Severity: High
Advisory: CVE-2026-48486
Aliases: GHSA-4vjp-2m22-r2q9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:H/A:L)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-48486
Type: osv

## Details
Signum Node is a HDD-mined cryptocurrency using an energy efficient and fair Proof-of-Commitment (PoC+) consensus algorithm. Prior to version 3.9.9, an integer overflow in BlockServiceImpl.applyBlock() allowed a miner to receive an arbitrarily inflated block reward by crafting a block with a negative totalFeeCashBackNqt value. The vulnerability was introduced when the SMART_FEES hardfork (block ~1,029,000) enabled fee cash-back and burn accounting without overflow protection. This issue has been patched in version 3.9.9.

## References
- https://github.com/signum-network/signum-node/releases/tag/v3.9.9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48486.json
- https://github.com/signum-network/signum-node/security/advisories/GHSA-4vjp-2m22-r2q9
- https://nvd.nist.gov/vuln/detail/CVE-2026-48486
