# [M] Possible Sandwich/MEV Attacks To Collect Most Rewards

## Summary
Severity: Medium
Contest weight: 0.4617
Dataset id: 12371
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function _harvest(address callFeeRecipient) internal whenNotPaused {
    gauge.getReward();
    uint256 outputBal = IERC20Upgradeable(output).balanceOf(address(this));
    if (outputBal > 0) {
        chargeFees(callFeeRecipient);
        addLiquidity();
        uint256 wantHarvested = balanceOfWant();
        uint256 _toProtocol;
        if (protocolFee > 0) {
            _toProtocol = wantHarvested * protocolFee / PERCENTAGE;
            totalProtocolFee += _toProtocol;
            want.transfer(protocolReceiver, _toProtocol);
        }
        totalHarvested += wantHarvested - _toProtocol;
        deposit();
        lastHarvest = block.timestamp;
        emit StratHarvest(msg.sender, wantHarvested, balanceOf());
    }
}

function addLiquidity() internal {
    uint256 outputBal = IERC20Upgradeable(output).balanceOf(address(this));
    uint256 lp0Amt = outputBal / 2;
    uint256 lp1Amt = outputBal - lp0Amt;
    ISolidlyRouter router = ISolidlyRouter(uniRouter);
    if (stable) {
        uint256 out0 = lp0Amt;
        if (lpToken0 != output) {
            out0 = (router.getAmountsOut(lp0Amt, outputToLp0Route)[outputToLp0Route.length - 1] * 1e18) / lp0Decimals;
        }
        uint256 out1 = lp1Amt;
        if (lpToken1 != output) {
            out1 = (router.getAmountsOut(lp1Amt, outputToLp1Route)[outputToLp1Route.length - 1] * 1e18) / lp1Decimals;
        }
        (uint256 amountA, uint256 amountB, ) = router.quoteAddLiquidity(
            lpToken0,
            lpToken1,
            stable,
            out0,
            out1
        );
        amountA = (amountA * 1e18) / lp0Decimals;
        amountB = (amountB * 1e18) / lp1Decimals;
        uint256 ratio = (((out0 * 1e18) / out1) * amountB) / amountA;
        lp0Amt = (outputBal * 1e18) / (ratio + 1e18);
        lp1Amt = outputBal - lp0Amt;
        if (lpToken0 != output) {
            router.swapExactTokensForTokens(
                lp0Amt,
                0,
                outputToLp0Route,
                address(this),
                block.timestamp
            );
        }
        if (lpToken1 != output) {
            router.swapExactTokensForTokens(
                lp1Amt,
                0,
                outputToLp1Route,
                address(this),
                block.timestamp
            );
        }
        uint256 lp0Bal = IERC20Upgradeable(lpToken0).balanceOf(address(this));
        uint256 lp1Bal = IERC20Upgradeable(lpToken1).balanceOf(address(this));
        router.addLiquidity(
            lpToken0,
            lpToken1,
            stable,
            lp0Bal,
            lp1Bal,
            address(this),
            block.timestamp
        );
    }
}
```
The KOL protocol has designed a new strategy contract to invest user deposits (held in KolStrategyThena), harvest growing yields, and collect any gains, if any, to the share holders. In the meantime, we notice the protocol takes a different approach by directly rewarding the yields back to investors. To elaborate, we show below the _harvest() function in KolStrategyThena. This routine essentially collects any pending rewards via gauge::getReward() (line 211) and then distributes the collected rewards evenly to current share holders. We notice the collected rewards are evenly distributed to share holders. With that, it is possible for a malicious actor to launch a flashloan-assisted deposit to claim the majority of rewards, resulting in significantly less rewards to legitimate share holders. This is possible as the harvest() may be triggered in a permissionless manner, allowing for a crafted contract to directly borrow a flashloan, deposit the borrowed loan into the vault pool, call harvest() to claim a majority share in rewards, and finally return the flashloan. In the meantime, the current protocol supports the conversion of output token to others as liquidity. Because of that, there is a constant need of swapping one asset to another. With that, the protocol has provided a helper routine addLiquidity(). To elaborate, we show above the helper routine. We notice the conversion is routed to Thena router in order to swap one asset to another. And the swap operation does not specify any restriction on possible slippage and is therefore vulnerable to possible front-running attacks, resulting in a smaller gain for this round of conversion. Note that this is a common issue plaguing current AMM-based DEX solutions. Specifically, a large trade may be sandwiched by a preceding sell to reduce the market price, and a tailgating buy-back of the same amount plus the trade amount. Such sandwiching behavior unfortunately causes a loss and brings a smaller return as expected to the trading user because the swap rate is lowered by the preceding sell. As a mitigation, we may consider specifying the restriction on possible slippage caused by the trade or referencing the TWAP or time-weighted average price of UniswapV2. Nevertheless, we need to acknowledge that this is largely inherent to current blockchain infrastructure and there is still a need to continue the search efforts for an effective defense.

## Recommendation
Develop an effective mitigation to the above sandwich attack, including the use of slippage control to the above front-running attack to better protect the interests of farming users.
