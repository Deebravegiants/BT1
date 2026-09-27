# [M] Using `setBigBangEthMarketDebtRate` or `setBigBangConfig` cause incorrect interest calculation due to retroactively applying the interest rate

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-tapioca
Published: 2023-08-04
Source: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1277
Type: code-finding

## Details
# Lines of code

https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/bigBang/BigBang.sol#L515


# Vulnerability details

### Impact
Interest rates are computed by calculating the `debtRate` and multiplying it by `elapsedTime`
https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/bigBang/BigBang.sol#L515

```solidity
uint256 elapsedTime = block.timestamp - _accrueInfo.lastAccrued;
```

You can visualize this as a Linear Chart where time is on the X axis and the slope of the line is the `debtRate`

Because of how `setBigBangEthMarketDebtRate` and `setBigBangConfig` are written, these functions will not accrue the interest that has passed before changing the slope of the `debtRate`.

This has a side effect at all time:
- The interest math for the pending interest will be computed incorrectly

Additionally, if the interest is made to raise too sharply, this can also cause some positions to be unfairly liquidated due to the newly accrued interest which will be magnified by the `elapsedTime` 


https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/Penrose.sol#L256-L259
```solidity
    function setBigBangEthMarketDebtRate(uint256 _rate) external onlyOwner {
        bigBangEthDebtRate = _rate;
        emit BigBangEthMarketDebtRate(_rate);
    }
```

Changing `bigBangEthDebtRate` via `setBigBangEthMarketDebtRate` will not update the debt of the `ethMarket`, this means that accounts that 

will not accrue other markets nor the ETh market, changing it will cause a loss of Yield or Potentially underwater positions

### POC

#### Example

- Imagine a 1% per day interest
- 2 days elapse
- The interest would be computed as 2%
- The `bigBangEthDebtRate` is called to cause the new interest to be 2% per day
- Technically the new interest should start from today
- 1 more day elapse

- Intended result = 2% + 2% = 4% interest (ignoring compounding for simplicity)

- Actual result = 3 days * 3% = 9% of interest due to accrual "going in the past"

#### Visualization

The visualization illustrates the issue:
https://miro.com/app/board/uXjVMwwR4JY=/?share_link_id=757290249679


### Further Resources
https://github.com/code-423n4/2023-01-reserve-findings/issues/287

### Mitigation

I recommend centralizing the interest rate logic to allow bulk accrual of markets, if that's not possible you would want to at least rewrite the function to allow accruing markets before changing setters


## Assessed type

Invalid Validation
