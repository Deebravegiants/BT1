# [M] `getDebtRate()` is view and reads `ethMarket.getTotalDebt` allowing for manipulations

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-tapioca
Published: 2023-08-04
Source: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1561
Type: code-finding

## Details
# Lines of code

https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/bigBang/BigBang.sol#L180-L201


# Vulnerability details

### Impact
Each `BingBang` market is an independent deployment

The interest rate for each market is computed via [`getDebtRate`](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/bigBang/BigBang.sol#L180), which compares the "utilization" of the `ethMarket` against the specific `market`

https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/bigBang/BigBang.sol#L180-L201

```solidity
function getDebtRate() public view returns (uint256) {
        if (_isEthMarket) return penrose.bigBangEthDebtRate(); // default 0.5%
        if (totalBorrow.elastic == 0) return minDebtRate;

        uint256 _ethMarketTotalDebt = BigBang(penrose.bigBangEthMarket())
            .getTotalDebt();
        uint256 _currentDebt = totalBorrow.elastic;
        uint256 _maxDebtPoint = (_ethMarketTotalDebt *
            debtRateAgainstEthMarket) / 1e18;

        if (_currentDebt >= _maxDebtPoint) return maxDebtRate;

        uint256 debtPercentage = ((_currentDebt - debtStartPoint) *
            DEBT_PRECISION) / (_maxDebtPoint - debtStartPoint);
        uint256 debt = ((maxDebtRate - minDebtRate) * debtPercentage) /
            DEBT_PRECISION +
            minDebtRate;

        if (debt > maxDebtRate) return maxDebtRate;

        return debt;
    }
```

Because of the fact that a change in `ethMarket.getTotalDebt()` doesn't cause any accrual in other `BigBank` markets, an attacker can, at times, manipulate the `debtRate` by:

- Flashloaning ETH
- Providing ETH
- Getting Debt on the ETH market
- Calling `_accrue` on the specific market they are invested in

This can be done profitably any time the interest that is yet to tick is lower than the borrowing cost (5 BPS).

For context, paying 30% yearly
`30 / 365 = 0.08219178082` 8.2 BPS per day

Meaning that for most Whales, if even one day has passed without any interest ticking, it can be profitable to manipulate the interest rate to save on fees rather than pay the proper accrual value.


### POC

- Whale has to move their Singularity Position
- Realize more than 8BPS of interest will accrue
- Provide equivalent Cost / 5 BPS / LTV of ETH to the Eth Market
- Mint for that amount
- Accrue their own debt, at discounted rate

In the case of a few days of not accrue or higher interest rates, this becomes a valid strategy even when done via paid flashloans

### Mitigation Steps
Centralizing (perhaps in Penrose) the interest rate logic would allow to re-accrue the debt of all markets when the ETH market debt changes

This would avoid these type of "Cross Contract" view manipulations


## Assessed type

Invalid Validation
