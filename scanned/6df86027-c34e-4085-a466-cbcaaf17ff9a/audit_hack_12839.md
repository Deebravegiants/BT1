# [M] Univ3Twap isn’t deployed on Arbitrum

## Summary
Severity: Medium
Reporter: twicek
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L49
Type: audit-issue

## Details
# Univ3Twap isn’t deployed on Arbitrum

## Summary

## Vulnerability Detail

`Univ3Twap` contract should be deployed at the `TWAP` address but isn’t.

[Dca.vy#L49](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L49)

```solidity
TWAP: constant(address) = 0xFa64f316e627aD8360de2476aF0dD9250018CFc5
```

Thus, `_calc_min_amount_out` will revert at this line:

[Dca.vy#L268](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L268)

```solidity
twap_value: uint256 = Univ3Twap(TWAP).getTwap(_path, _fees, _twap_length)
```

## Impact

Any function calling `_calc_min_amount_out`  will revert.

## Code Snippet
[Dca.vy#L49](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L49)
[Dca.vy#L268](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L268)

## Tool used

Manual Review

## Recommendation

Modify the hard-coded address to a deployed address.
