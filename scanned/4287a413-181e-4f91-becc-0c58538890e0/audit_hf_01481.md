# [M] `RubiconMarket.sol#isClosed`

## Summary
Severity: Medium
Contest weight: 0.5420
Dataset id: 7852
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function isClosed() public pure returns (bool closed) {
    return false;
}
```

After close, no new buys are allowed.

Based on context and comments, when the market is closed, offers can only be cancelled (offer and buy will throw).

However, in the current implementation, `isClosed()` always returns `false`, so the checks on whether the market is closed will always pass. (E.g: `can_offer()`, `can_buy()`, etc)

And there is a storage variable called `stopped`, but it’s never been used, which seems should be used for `isClosed`.

## Recommendation
Change to:
    
```solidity
    function isClosed() public pure returns (bool closed) {
        return stopped;
    }
```

Intended functionality - confirmed
