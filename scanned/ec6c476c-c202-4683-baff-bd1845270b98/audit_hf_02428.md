# [M] Reentrancy Risk In MultisigWallet::execute()

## Summary
Severity: Medium
Contest weight: 0.4590
Dataset id: 13039
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A common coding best practice in Solidity is the adherence of checks-effects-interactions principle. This principle is effective in mitigating a serious attack vector known as re-entrancy. Via this particular attack vector, a malicious contract can be reentering a vulnerable contract in a nested manner. Specifically, it first calls a function in the vulnerable contract, but before the first instance of the function call is finished, second call can be arranged to re-enter the vulnerable contract by invoking functions that should only be executed once. This attack was part of several most prominent hacks in Ethereum history, including the DAO [12] exploit, and the recent Uniswap/Lendf.Me hack [11]. We notice there are several occasions the checks-effects-interactions principle is violated. Note the collectFees() function (see the code snippet below) is provided to externally call a token contract to transfer assets. However, the invocation of an external contract requires extra care in avoiding the above re-entrancy. Apparently, the interaction with the external contract (lines 503-504) starts before effecting the update on internal states (lines 511-512), hence violating the principle. In this particular case, if the external contract has certain hidden logic that may be capable of launching re-entrancy via the very same collectFees() function.
```solidity
function collectFees(uint256 amount0, uint256 amount1) external updateVault(msg.sender) {
    UserInfo storage user = userInfo[msg.sender];
    require(user.token0Rewards >= amount0, "A0");
    require(user.token1Rewards >= amount1, "A1");
    uint256 balance0 = _balance0();
    uint256 balance1 = _balance1();
    if (balance0 >= amount0 && balance1 >= amount1) {
        if (amount0 > 0) pay(token0, address(this), msg.sender, amount0);
        if (amount1 > 0) pay(token1, address(this), msg.sender, amount1);
    } else {
        uint128 liquidity = pool03.liquidityForAmounts(amount0, amount1, tickLower, tickUpper);
        (amount0, amount1) = pool03.burnExactLiquidity(tickLower, tickUpper, liquidity, msg.sender);
    }
    user.token0Rewards = user.token0Rewards.sub(amount0);
    user.token1Rewards = user.token1Rewards.sub(amount1);
    emit RewardPaid(msg.sender, amount0, amount1);
}
```

## Recommendation
Add the nonReentrant modifier to prevent reentrancy.
