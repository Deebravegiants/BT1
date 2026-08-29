# [M] FeeBuyback's submit can lose funds if used with zero addresses, which is allowed

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-telcoin
Published: 2022-11-22
Source: https://github.com/sherlock-audit/2022-11-telcoin-judging/issues/97
Type: sherlock-finding

## Details
hyh

medium

# FeeBuyback's submit can lose funds if used with zero addresses, which is allowed

## Summary

It's now allowed to use FeeBuyback's submit() with zero `wallet` or zero `_aggregator`, while low level calls are performed with both addresses.

## Vulnerability Detail

Low-level calls submit() perform will return success if used with zero addresses as the failure need to come from the contract that is being called, while zero address will not do that. In both cases no operations will be performed.

## Impact

Not executing the primary swap, but paying the fee is the fund loss for an owner.

Executing the primary swap, but not paying the fee as there is no TEL on the balance is the fund loss for a recipient.

Also, when MATIC is used the native funds sent to zero address via `_aggregator.call{value: msg.value}(swapData)` end up being lost.

## Code Snippet

Both `_aggregator` (in constructor) and `wallet` (in submit() below) aren't checked to be non-zero:

https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L28-L33

```solidity
  constructor(address aggregator_, address safe_, IERC20 telcoin_, ISimplePlugin referral_) TieredOwnership() {
    _aggregator = aggregator_;
    _safe = safe_;
    _telcoin = telcoin_;
    _referral = referral_;
  }
```

Low-level calls submit() perform will be successful if the address called (`wallet`, or `_aggregator` later) is zero:

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-telcoin-judging/issues/97_
