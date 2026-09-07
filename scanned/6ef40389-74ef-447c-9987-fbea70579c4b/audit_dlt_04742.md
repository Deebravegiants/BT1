# [M] epochsByBuyer() count error

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-09-knox
Published: 2022-10-18
Source: https://github.com/sherlock-audit/2022-09-knox-judging/issues/107
Type: sherlock-finding

## Details
bin2chen

medium

# epochsByBuyer() count error

## Summary
In Auction.sol cancelLimitOrder()
When removing the user's epochs array without determining whether there are other orders in the same epoch, just removed directly, resulting in counting errors.

## Vulnerability Detail
In the same epoch, the user can have more than one order, when one of the orders is removed, "epochsByBuyer[buyer].remove(epoch_id)" is removed, but there are actually other orders in this epoch

## Impact
epochsByBuyer() count error

## Code Snippet
https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/Auction.sol#L220

```solidity 
    function cancelLimitOrder(uint64 epoch, uint256 id) external nonReentrant {
        ...
        l.epochsByBuyer[data.buyer].remove(epoch); /*** don't check this epoch has other order ***/

    }
```

## Tool used

Manual Review

## Recommendation

```solidity
    function cancelLimitOrder(uint64 epoch, uint256 id) external nonReentrant {
...

        require(data.buyer != address(0), "order does not exist");
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-09-knox-judging/issues/107_
