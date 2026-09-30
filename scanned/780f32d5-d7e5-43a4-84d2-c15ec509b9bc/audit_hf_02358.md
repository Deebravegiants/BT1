# [M] Possible Costly lp_token From Improper Staking Initialization

## Summary
Severity: Medium
Contest weight: 0.4626
Dataset id: 12784
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The ERC20Staking contract allows users to stake the supported target_token tokens and get in return lp_token tokens to represent the pool shares. While examining the share calculation with the given stakes, we notice an issue that may unnecessarily make the pool token extremely expensive and bring hurdles (or even causes loss) for later stakers. To elaborate, we show below the related code snippet of the ERC20Staking contract. The stake() routine is used for participating users to stake the supported asset and get respective lp_token in return. The issue occurs when the pool is being initialized under the assumption that the current pool is empty.
```solidity
function stake(uint256 _amount) public returns(uint256){
    uint256 amount = 0;
    uint256 prev = IERC20(target_token).balanceOf(address(this));
    IERC20(target_token).safeTransferFrom(msg.sender, address(this), _amount);
    amount = IERC20(target_token).balanceOf(address(this)).safeSub(prev);
    if(amount == 0){
        return 0;
    }
    uint256 lp_amount = 0;
    if(IERC20(lp_token).totalSupply() == 0){
        lp_amount = amount.safeMul(uint256(10) ** ERC20Base(lp_token).decimals()).safeDiv(uint256(10) ** ERC20Base(target_token).decimals());
    }else{
        uint256 t2 = IERC20(lp_token).totalSupply();
        lp_amount = amount.safeMul(t2).safeDiv(prev);
        if(lp_amount == 0){
            return 0;
        }
    }
    TokenInterface(lp_token).generateTokens(msg.sender, lp_amount);
    if(address(callback) != address(0x0)){
        callback.onStake(msg.sender, amount, lp_amount);
    }
    emit ERC20Stake(msg.sender, amount, lp_amount);
    return lp_amount;
}
```
Specifically, when the pool is being initialized, the lp_amount share value directly takes the value of amount (line 52), which is under control by the malicious actor. As this is the first stake, the current total supply equals the calculated lp_amount = amount.safeMul(uint256(10)**ERC20Base(lp_token).decimals()).safeDiv(uint256(10)**ERC20Base(target_token).decimals())= 1WEI. With that, the actor can further transfer a huge amount of target_token tokens to ERC20Staking contract with the goal of making the lp_token extremely expensive. An extremely expensive pool token can be very inconvenient to use as a small number of 1WEI may denote a large value. Furthermore, it can lead to precision issue in truncating the computed pool tokens for staked assets. If truncated to be zero, the staked assets are essentially considered dust and kept by the pool without returning any pool tokens. This is a known issue that has been mitigated in popular Uniswap. When providing the initial liquidity to the contract (i.e. when totalSupply is 0), the liquidity provider must sacrifice 1000 LP tokens (by sending them to address(0)). By doing so, we can ensure the granularity of the LP tokens is always at least 1000 and the malicious actor is not the sole holder. This approach may bring an additional cost for the initial liquidity provider, but this cost is expected to be low and acceptable.

## Recommendation
Revise current execution logic of stake() to defensively calculate the share amount when the pool is being initialized. An alternative solution is to ensure guarded launch that safeguards the first stake to avoid being manipulated.
