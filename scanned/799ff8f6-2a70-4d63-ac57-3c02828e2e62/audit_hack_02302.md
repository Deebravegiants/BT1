# [M] \[M06\] `Reservoir` does not accept `ETH`

## Summary
Severity: Medium
Source: https://github.com/notional-finance/contracts-v2/blob/c37c89c9729b830637558a09b6f22fc6a735da64/contracts/external/governance/Reservoir.sol#L14
Type: audit-issue

## Details
The [Reservoir contract](https://github.com/notional-finance/contracts-v2/blob/c37c89c9729b830637558a09b6f22fc6a735da64/contracts/external/governance/Reservoir.sol#L14) has no way to accept `ETH`, even though governance can [execute proposals](https://github.com/notional-finance/contracts-v2/blob/c37c89c9729b830637558a09b6f22fc6a735da64/contracts/external/governance/GovernorAlpha.sol#L280-L285) that handle `ETH`.

Whether the `Reservoir` contract should handle `ETH` or not, for instance by using `WETH` instead of `ETH`, this expectation should be properly documented. Consider either implementing the functionality to allow the `Rerservoir` contract to handle and drip `ETH` or documenting the reasons behind this choice.

_**Update:** Fixed in [pull request 24](https://github.com/notional-finance/contracts-v2/pull/24/files) by adding documentation about the design choice._
