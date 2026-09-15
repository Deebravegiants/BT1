# [H] CVE-2021-25837

## Summary
Severity: High
Advisory: CVE-2021-25837
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2021-02-08
Source: https://osv.dev/vulnerability/CVE-2021-25837
Type: osv

## Details
Cosmos Network Ethermint <= v0.4.0 is affected by cache lifecycle inconsistency in the EVM module. Due to the inconsistency between the Storage caching cycle and the Tx processing cycle, Storage changes caused by a failed transaction are improperly reserved in memory. Although the bad storage cache data will be discarded at EndBlock, it is still valid in the current block, which enables many possible attacks such as an "arbitrary mint token".

## References
- https://github.com/cosmos/ethermint/issues/667#issuecomment-759284107
