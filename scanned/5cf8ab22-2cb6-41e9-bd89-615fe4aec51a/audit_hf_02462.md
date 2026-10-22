# [M] Possibly Inaccurate Interest Accrual in CErc20

## Summary
Severity: Medium
Contest weight: 0.4597
Dataset id: 13194
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Tender.fi protocol provides incentive mechanisms with the support of autocompounding and collateralization for popular DeFi assets, starting with GMX and GLP. While examining the autocompounding feature, we notice the current implementation may result in inaccurate interest accrual. To elaborate, we show below the compoundFresh() function. As the name indicates, this function is added to support GLP-related autocompounding. Note that the accrualBlockNumber storage variable records the latest block number for interest accrual. However, this function is exposed even for non-GLP tokens and may be abused to simply update accrualBlockNumber without actually collecting any interest!

```solidity
function compoundFresh() internal {
    if (totalSupply == 0) {
        return;
    }
    // Remember the initial block number
    uint currentBlockNumber = getBlockNumber();
    uint accrualBlockNumberPrior = accrualBlockNumber;
    uint _glpBlockDelta = sub_(currentBlockNumber, accrualBlockNumberPrior);
    if (_glpBlockDelta < autoCompoundBlockThreshold) {
        return;
    }
    glpBlockDelta = _glpBlockDelta;
    prevExchangeRate = exchangeRateStoredInternal();
    // There is a new GLP Reward Router just for minting and burning GLP.
    /// https://medium.com/@gmx.io/gmx-deployment-updates-nov-2022-16572314874d
    IGmxRewardRouter newRewardRouter = IGmxRewardRouter(0xB95DB5B167D75e6d04227CfFFA61069348d271F5);
    glpRewardRouter.handleRewards(true, false, true, true, true, true, false);
    uint ethBalance = EIP20Interface(WETH).balanceOf(address(this));
    // if this is a GLP cToken, claim the ETH and esGMX rewards and stake the esGMX Rewards
    if (ethBalance > 0) {
        uint ethperformanceFee = div_(mul_(ethBalance, performanceFee), 10000);
        uint ethToCompound = sub_(ethBalance, ethperformanceFee);
        EIP20Interface(WETH).transfer(admin, ethperformanceFee);
        newRewardRouter.mintAndStakeGlp(WETH, ethToCompound, 0, 0);
    }
    accrualBlockNumber = currentBlockNumber;
}
```

## Recommendation
Revise the above compoundFresh() function to ensure it performs noop for non-GLP tokens.
