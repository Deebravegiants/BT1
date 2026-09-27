# [H] Wrong leverage calculation will lead to bad debts and bypassing liquidations

## Summary
Severity: High
Reporter: TheNaubit
Source: https://github.com/sherlock-audit/2022-08-sentiment-judging/blob/main/019-H/019-h.md
Type: audit-issue

## Details
# Wrong leverage calculation will lead to bad debts and bypassing liquidations

## Summary
A wrong decimals calculation in the `_effective_leverage` will lead bad debts and bypassing liquidations in some token pairs.

## Vulnerability Detail
In the `Vault` contract, the function `_effective_leverage` is used by several other functions to handle things like liquidations and bad debts. This function calculates the current leverage of a position based on the position's current value, the underlying margin and the accrued debt.

But the thing is the function uses three vars:
- `debt_value`, which is the USD value of the debt in the position using the debt token
- `margin_value`, which is the USD value of the margin in the position using the debt token
- `position_value`, which is the USD value of the position using the position token

All those values are obtained using Chainlink Price Feeds which typically returns a USD value with 8 decimals. So the protocol is calculating everything just like if every USD value has 8 decimals. But... there are some price feeds returning a USD value with more than 8 decimals (for example, the[ `AMPL / USD` feed has 18 decimals](https://etherscan.io/address/0xe20CA8D7546932360e37E9D72c1a47334af57706#readContract)).

So 3 cases can happen:
### 1. The ideal case: the debt token USD decimals are equal to the position value decimals
In this case, everything will work as intended, but to make easier to follow the next two cases, I will show an example.
Let's say `position_value` is `8e8` USD, `debt_value` is `2e8` USD and `margin_value` is `4e8`.

The returned value will be the result of the `_calculate_leverage` function:
`PRECISION * (2e8 + 4e8) / (8e8 - 2e8) / PRECISION` so basically it will return something like `1` (in this case, but usually it will return the right leverage amount, since this is the desired case).

You can try it in Solidity:
```solidity
    uint256 public constant PRECISION = 1e18;
    function test_case1() public pure returns (uint256) {
        uint256 _debt_value = 2e8;
        uint256 _margin_value = 4e8;
        uint256 _position_value = 8e8;

        return (
        PRECISION
        * (_debt_value + _margin_value)
        / (_position_value - _debt_value)
        / PRECISION
        );
        // It should return 1
    }
```

### 2. If the debt token USD decimals are greater than the position value decimals
Let's say `position_value` is `8e8` USD, `debt_value` is `2e18` USD and `margin_value` is `4e18`.

The returned value will be the result of the `_calculate_leverage` function:
`PRECISION * (2e18 + 4e18) / (8e8 - 2e18) / PRECISION` so basically it will always revert, making imposible to get its current leverage!

You can try it in Solidity:
```solidity
    uint256 public constant PRECISION = 1e18;
    function test_case2() public pure returns (uint256) {
        uint256 _debt_value = 2e18;
        uint256 _margin_value = 4e18;
        uint256 _position_value = 8e8;

        return (
        PRECISION
        * (_debt_value + _margin_value)
        / (_position_value - _debt_value)
        / PRECISION
        );
        // It reverts
    }
```

### 3. If the debt token USD decimals are lesser than the position value decimals
Let's say `position_value` is `8e8` USD, `debt_value` is `2e2` USD and `margin_value` is `4e2`.

The returned value will be the result of the `_calculate_leverage` function:
`PRECISION * (2e2 + 4e2) / (8e8 - 2e2) / PRECISION` so basically it will always return 0, making the position to be able to accrue an infinite amount of bad debt without being liquidated!

You can try it in Solidity:
```solidity
    uint256 public constant PRECISION = 1e18;
    function test_case3() public pure returns (uint256) {
        uint256 _debt_value = 2e2;
        uint256 _margin_value = 4e2;
        uint256 _position_value = 8e8;

        return (
        PRECISION
        * (_debt_value + _margin_value)
        / (_position_value - _debt_value)
        / PRECISION
        );
        // It returns 0
    }
```

Related and similar issues in the past: https://github.com/sherlock-audit/2022-08-sentiment-judging/blob/main/019-H/019-h.md

## Impact
By reverting always when calculating the leverage or always returning 0 as the effective leverage; this will break several core protocol functions. It will break the `_calculate_leverage`, `_effective_leverage`, `effective_leverage`, `_is_liquidatable`, `is_liquidatable`, `remove_margin`, `reduce_position` and **`liquidate`** functions in the `Vault` contract.

## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L465-L477

## Tool used
Manual Review

## Recommendation
The best solution is to perform some normalization to the USD value obtained from the Chainlink price feeds. For example, standardizing all the USD values to 8 decimals.

In the [`_to_usd_oracle_price` function](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L562) a check could be implemented by checking the `decimals()` function every Chainlink Price Feed oracle implements ([for example in the AMPL / USD feed](https://etherscan.io/address/0xe20CA8D7546932360e37E9D72c1a47334af57706#readContract#F3)) and then performing a conversion of the returned values to the standardized 8 decimals.
