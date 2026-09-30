# [H] CVE-2021-25835

## Summary
Severity: High
Advisory: CVE-2021-25835
Aliases: GHSA-x5f3-qmwj-4f84, GO-2022-0889
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2021-02-08
Source: https://osv.dev/vulnerability/CVE-2021-25835
Type: osv

## Details
Cosmos Network Ethermint <= v0.4.0 is affected by a cross-chain transaction replay vulnerability in the EVM module. Since ethermint uses the same chainIDEpoch and signature schemes with ethereum for compatibility, a verified signature in ethereum is still valid in ethermint with the same msg content and chainIDEpoch, which enables "cross-chain transaction replay" attack.

## References
- https://github.com/cosmos/ethermint/issues/687
- https://github.com/cosmos/ethermint/pull/692
