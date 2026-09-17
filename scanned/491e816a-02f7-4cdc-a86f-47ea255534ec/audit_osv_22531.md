# [M] Discrepency in transfer value and actual value due to incorrect truncation in Frontier

## Summary
Severity: Medium
Advisory: CVE-2022-31111
Aliases: GHSA-hc8w-mx86-9fcj
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2022-07-06
Source: https://osv.dev/vulnerability/CVE-2022-31111
Type: osv

## Details
Frontier is Substrate's Ethereum compatibility layer. In affected versions the truncation done when converting between EVM balance type and Substrate balance type was incorrectly implemented. This leads to possible discrepancy between appeared EVM transfer value and actual Substrate value transferred. It is recommended that an emergency upgrade to be planned and EVM execution temporarily paused in the mean time. The issue is patched in Frontier master branch commit fed5e0a9577c10bea021721e8c2c5c378e16bf66 and polkadot-v0.9.22 branch commit e3e427fa2e5d1200a784679f8015d4774cedc934. This vulnerability affects only EVM internal states, but not Substrate balance states or node. You can temporarily pause EVM execution (by setting up a Substrate `CallFilter` that disables `pallet-evm` and `pallet-ethereum` calls before the patch can be applied.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/31xxx/CVE-2022-31111.json
- https://github.com/paritytech/frontier/security/advisories/GHSA-hc8w-mx86-9fcj
- https://nvd.nist.gov/vuln/detail/CVE-2022-31111
- https://github.com/paritytech/frontier/commit/e3e427fa2e5d1200a784679f8015d4774cedc934
- https://github.com/paritytech/frontier/commit/fed5e0a9577c10bea021721e8c2c5c378e16bf66
- https://github.com/paritytech/frontier/pull/753
