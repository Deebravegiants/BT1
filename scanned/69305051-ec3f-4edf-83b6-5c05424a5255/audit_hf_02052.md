# [M] Possible Costly StakeToken From Improper Pool Initialization

## Summary
Severity: Medium
Contest weight: 0.4604
Dataset id: 11681
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned earlier, the Augmented Finance protocol will reward participating users if they stake their tokens to receive pro-rata staking rewards. In order to prevent possible flashloan-assisted front-running attacks that may claim the majority of rewards, the staking logic is designed to have a cooldown period for staked assets. To elaborate, we show below the internalStake() routine. This routine is used for liquidity providers to deposit desired liquidity and get respective pool tokens in return. The issue occurs when the pool is being initialized under the assumption that the current pool is empty.
```solidity
function internalStake(
    address from,
    address to,
    uint256 underlyingAmount,
    uint256 referral,
    bool transferFrom
) internal returns (uint256 stakeAmount) {
    require(underlyingAmount > 0, Errors.VL_INVALID_AMOUNT);
    uint256 oldReceiverBalance = balanceOf(to);
    stakeAmount = underlyingAmount.percentDiv(exchangeRate());
    _stakersCooldowns[to] = getNextCooldown(0, stakeAmount, to, oldReceiverBalance);
}

function exchangeRate() public view override returns (uint256) {
    uint256 total = totalSupply();
    if (total == 0) {
        return PercentageMath.ONE; // 100%
    }
    return _stakedToken.balanceOf(address(this)).percentOf(total);
}
```
Specifically, when the pool is being initialized, the share value directly takes the exchange rate of PercentageMath.ONE (line 231). As this is the first deposit, the current total supply equals the calculated stakeAmount = underlyingAmount.percentDiv(exchangeRate()) = 1WEI. After that, the actor can further transfer a huge amount of _stakedToken with the goal of making the pool token extremely expensive. An extremely expensive pool token can be very inconvenient to use as a small number of 1WEI may denote a large value. Furthermore, it can lead to a precision issue in truncating the computed pool tokens for deposited assets. If truncated to be zero, the deposited assets are essentially considered dust and kept by the pool without returning any pool tokens. This is a known issue that has been mitigated in popular UniswapV2. When providing the initial liquidity to the contract (i.e. when totalSupply is 0), the liquidity provider must sacrifice 1000 LP tokens (by sending them to address(0)). By doing so, we can ensure the granularity of the LP tokens is always at least 1000 and the malicious actor is not the sole holder. This approach may bring an additional cost for the initial stake provider, but this cost is expected to be low and acceptable. Another alternative requires a guarded launch to ensure the pool is always initialized properly.

## Recommendation
Revise current execution logic of stake() to defensively calculate the share amount when the pool is being initialized.
