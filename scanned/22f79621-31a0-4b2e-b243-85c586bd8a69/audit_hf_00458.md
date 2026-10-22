# [M] The reserve fee is calculated incorrectly

## Summary
Severity: Medium
Contest weight: 0.2609
Dataset id: 1887
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The reserve fee is calculated incorrectly leading to loss of fees for the reserve. The actual minted shares will represent a lower value than the set reserveFeeRate represents.
In ReserveLogic._mintToTreasury the calculation of shares uses reserveToETokenExchangeRate(reserve) to calculate the shares represented by the set reserveFeeRate
s/contracts/libraries/logic/ReserveLogic.sol#L217-L246
The issue is that minting of shares will increase the total supply of eTokens and therefore lead to the shares minted actually representing a lower value of underlying that was intended.
Internal pre-conditions
External pre-conditions
Attack Path
Lets consider the following values and use them in the _mintToTreasury function:
currentDebt = 2000e18 previousDebt = 1000e18 totalDebtAccrued = currentDebt.sub(previousDebt) = 2000e18-1000e18=1000e18 reserveValueAccrued = totalDebtAccrued.mul(feeRate).div(Constants.PERCENT_100) = (1000e18*1500)/10000=150e18
totalLiquidity = 10000e18 totalETokens = 5000e18 exchangeRate = reserveToETokenExchangeRate(reserve) = (5000e18*1e18)/10000e18=0.5e18 feeInEToken = reserveValueAccrued.mul(exchangeRate).div(Precision.FACTOR1E18) = (150e18*0.5e18)/1e18=75e18
This means that the treasury will get minted 75e18 shares which are meant to represent 150e18 of the underlying. This is however flawed because after minting, the totalETokens now become 5000e18+75e18=5075e18 after the minted shares are added.
If the treasury shares are claimed, the exchange rate would be:
totalLiquidity.mul(Precision.FACTOR1E18).div(totalETokens) = (10000e18*1e18)/5075e18 and the value of underlying would therefore be:
underlyingTokenAmount = reserve.eTokenToReserveExchangeRate().mul(eTokenAmount).div(Precision.FACTOR1E18) = (((10000e18*1e18)/5075e18)*75e18)/1e18=147.78e18
This value is lower that the intended 150e18
The protocol loses some of the reserve fees every time an operation is done. This figure will progressively compound over time as more transactions are done.

## Recommendation
The shares to be minted by the treasury should be:
reserveValueAccrued.mul(totalETokens).div(totalLiquidity - reserveValueAccrued))
Applying this to our case scenario above, the treasury would get minted approximately:
150e18.mul(5000e18).div(10000e18-150e18)=76.14e18
Redeeming these shares would therefore result in:
(((10000e18*1e18)/5076.14e18)*76.14e18)/1e18=149.99e18
Which is now correct.
Disclaimers
project.
Usage of all smart contract software is at the respective users’ sole risk and is the users’ responsibility.
