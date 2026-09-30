# [M] Potential Sandwich Attacks To Maximize getTestaReward()/Minimize getTestaFee()

## Summary
Severity: Medium
Contest weight: 0.4603
Dataset id: 13229
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In order to encourage participation, the protocol is designed to reward users who periodically check in to activate() or progress the TestaFarm pool. The reasoning is the protocol needs to measure the latest liquidity every 5000 Ethereum blocks. In particular, if the latest liquidity is higher than the last checkpoint, the internal indicator will move forward 1 step; if the liquidity is lower than previous check point, indicator will move backward 1 step. On each activation, available ETH rewards are proportionally allocated for the users based on their deposits in the pool. And the user who successfully calls the activate() function first in each cycle will receive 10 USDT worth of TESTA in return as a reward. To elaborate, we show below the firstActivate() routine from the TestaFarm contract. By calling this routine, the pool can compute current liquidity (line 1067) and reward the caller with TESTA reward.
```solidity
function firstActivate() public onlyEOA nonReentrant
require(IERC20(jTesta).balanceOf(msg.sender) >= config.getJTestaAmount(), "Insufficient jTesta amount");
require(initStartBlock == startBlock);
Public
require(block.number >= initStartBlock, "Cannot activate until the specific block time arrive");
currentLiquidity = config.getLiquidity();
startBlock = block.number;
startLiquidity = currentLiquidity;
// send Testa to user who press activate button
safeTestaTransfer(msg.sender, config.getTestaReward());
/// @dev Return the amount of Testa wei rewarded if we are activate the progress function.
function getTestaReward() public view override returns(uint256)
uint112 _reserve0, uint112 _reserve1,) = pair.getReserves();
uint256 reserve = uint256(_reserve0).mul(1e18).div(uint256(_reserve1));
uint256 ethPerDollar = uint256(getLatestPrice()).mul(1e10); // 1e8
uint256 testaPerDollar = ethPerDollar.mul(1e18).div(reserve);
uint256 _activateReward = activateReward.mul(1e18);
uint256 testaAmount = _activateReward.mul(1e18).div(testaPerDollar);
return testaAmount;
```
We notice the reward amount is computed in a way that depends on current pool reserves on Uniswap. As a result, the current swap rate can be manipulated by powerful miners attacks. (Note that a flashloan attack may not be possible as the activate() is restricted to EOA accounts only. Note that this is a common issue plaguing current AMM-based DEX solutions. Specifically, a large trade may be sandwiched by a preceding sell to reduce the market price, and a tailgating buy-back of the same amount plus the trade amount. Such sandwiching behavior unfortunately causes a loss and brings a smaller return as expected to the trading user (or a larger reward to the user who calls activate() in our case). A similar issue is also present in another getTestaFee() routine. As a mitigation, we may consider specifying the restriction on possible surge on totalSupply or imposing certain lock time for the users to claim the rewards. Nevertheless, we need to acknowledge that this is largely inherent to current blockchain infrastructure and there is still a need to continue the search efforts for an effective defense.

## Recommendation
Develop an effective mitigation to the above sandwich attack to better protect the interests of liquidity providers.
