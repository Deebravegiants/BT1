# [M] M-04 Unmitigated

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-09-reserve-mitigation
Published: 2023-09-27
Source: https://github.com/code-423n4/2023-09-reserve-mitigation-findings/issues/19
Type: code-finding

## Details
# Lines of code

https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/erc20/RewardableERC20.sol#L86


# Vulnerability details

## Impact
The previously identified vulnerability of potential rounding issues during reward calculations has not been fully mitigated. The current strategy to keep remainders and use them in subsequent `_claimAndSyncRewards()` calls does not adequately address the issue when the `rewardToken` has a decimal smaller than 6 and/or the total reward tokens entailed is much smaller. This could lead to significant truncation losses as the remainder rolls over until it's large enough to overcome truncation, unfairly disadvantaging users, particularly those exiting the investment earlier, as they would miss out on a sizable amount of reward. This rounding issue, if left unresolved, can erode trust and potentially open up the system to arbitrage opportunities, further exacerbating the loss of rewards for regular users.

## PoC (Proof of Concept)
### Scenario
Let's assume `rewardToken` still has 6 decimals but there are only 0.5 million rewardToken to be distributed for the year and `_claimAndSyncRewards()` is called every minute. And, totalSupply = 10^6 with 18 decimals.

The expected rewards for 1 min are 500000 / 365 / 24 / 60 = 0.95 rewardToken = 950000 wei.

Initially, assume `balanceAfterClaimingRewards = 1950000` (wei), and `_previousBalance = 1000000` (wei), making `delta = 950000` (wei).

`deltaPerShare` will be calculated as:

(950000 * 10^18) / (10^6 * 10^18) = 0

Now, `balanceAfterClaimingRewards` is updated to:

previous balance + (deltaPerShare * totalSupply / one)
= 1000000 + (0 * (10^6 * 10^18) / 10^18)
= 1000000 + 0 = 1000000 (wei)   

As illustrated, the truncation issue causes `deltaPerShare` to equal `0`. This will lead to a scenario where the rewards aren't distributed accurately among users, particularly affecting those who exit earlier before the remainder becomes large enough to surpass truncation.

In a high-frequency scenario where `_claimAndSyncRewards` is invoked often, users could miss out on a significant portion of rewards, showcasing the inadequacy of the proposed mitigation in handling the rounding loss effectively.

## Mitigation
Using a bigger multiplier as the original report suggested seems viable, but finding a suitably discrete factor could be tricky.

While keeping the current change per [PR #896](https://github.com/reserve-protocol/protocol/pull/896), I suggest adding another step by normalizing both `delta` and `_totalSupply` to `PRICE_DECIMALS`, i.e. 18, that will greatly minimize the prolonged remainder rollover. The intended decimals may be obtained by undoing the normalization when needed. Here are the two useful functions (assuming `decimals` is between 1 to 18) that could help handle the issue but it will require further code refactoring on `_claimAndSyncRewards()` and `_syncAccount()`.   

```solidity
    /// @dev    Convert decimals of the value to price decimals
    function _toPriceDecimals(uint128 _value, uint8 decimals, address liquidityPool)
        internal
        view
        returns (uint256 value)
    {
        if (PRICE_DECIMALS == decimals) return uint256(_value);
        value = uint256(_value) * 10 ** (PRICE_DECIMALS - decimals);
    }

    /// @dev    Convert decimals of the value from the price decimals back to the intended decimals
    function _fromPriceDecimals(uint256 _value, uint8 decimals, address liquidityPool)
        internal
        view
        returns (uint128 value)
    {
        if (PRICE_DECIMALS == decimals) return _toUint128(_value);
        value = _toUint128(_value / 10 ** (PRICE_DECIMALS - decimals));
    }
```


## Assessed type

Decimal
