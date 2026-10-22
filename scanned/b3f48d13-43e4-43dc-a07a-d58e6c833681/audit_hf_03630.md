# [M] Lack of claim method for referral fee in GMX-

## Summary
Severity: Medium
Contest weight: 0.5937
Dataset id: 19699
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The referral fee airdropped to GMXFuturesPoolHedger will be lost.
The default referral fee code in GMXFuturesPoolHedger is set
```solidity
bytes32 public referralCode = bytes32("LYRA");
```
This referral code is used when used to create increase position position request.
```solidity
uint executionFee = _getExecutionFee();
bytes32 key = positionRouter.createIncreasePosition{value: executionFee}(
    path,
    address(baseAsset), // index token
    collateralDelta, // amount in via router is in the native currency decimals
    0, // min out
    _convertToGMXPrecision(sizeDelta),
    isLong,
    acceptableSpot,
    executionFee,
    referralCode,
    address(0)
);
```
According to GMX documentation:
https://gmxio.gitbook.io/gmx/referrals#tiers
If using referral code, the discount is applied
Tier 1: 5% discount for traders, 5% rebates to referrer
Tier 2: 10% discount for traders, 10% rebates to referrer
Tier 3: 10% discount for traders, 15% rebates to referrer paid ETH / AVAX, 5%
rebates to referrer paid esGMX
Rebates and discounts apply on the opening and closing fees for
leverage trading.
The opening and closing fees are 0.1% on GMX, there is no price impact
for trades and zero spread for tokens like BTC and ETH, rebates are
calculated before user discounts so referrers earn on the full maker fee
and from what would otherwise be spread on other exchanges. As a
result, referrers would earn equivalent amounts of rebates per volume on
GMX when compared to other referral programs.
of GMX is $30 the full 5% bonus can be paid for total Tier 3 referral
volumes up to $3 billion per week. esGMX tokens distributed for this
program will not require GMX or GLP to vest, the vault to vest the tokens
will be available towards the end of Q1 2023.
The price of esGMX will be based on the 7 day TWAP of GMX. Wallet
providers and other protocols will be eligible for Tier 2 and Tier 3
rewards as well.
The trader fee discount that is airdropped to the GMXFuturesPoolHedger contract
is lost because there is no such method in GMXFuturesPoolHedger to locked
ERC20 token.
The trader fee discount that is airdropped to the GMXFuturesPoolHedger contract
is lost because there is no such method in GMXFuturesPoolHedger to locked
ERC20 token.

## Recommendation
We recommend the project add a admin function to claim stucked ERC20 token
including the claiming the airdropped GMX trading fee refund.
