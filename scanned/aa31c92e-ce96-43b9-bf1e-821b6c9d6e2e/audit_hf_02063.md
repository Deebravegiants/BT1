# [M] Sandwich Attacks For SwapMining Rewards

## Summary
Severity: Medium
Contest weight: 0.5937
Dataset id: 11711
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The SwapMining protocol is forked from MDX and provides incentives when users make a swap. The protocol provides rewards based on the swapping amount for the supported assets. While examining the reward calculation with the given swap amount, we notice the takerWithdraw() may be sandwiched by two swaps with reversed paths. To elaborate, we show the SwapMining::takerWithdraw() routine.

```solidity
// The user withdraws all the transaction rewards of the pool
function takerWithdraw() public {
    uint256 userSub;
    uint256 length = poolInfo.length;
    for (uint256 pid = 0; pid < length; ++pid) {
        PoolInfo storage pool = poolInfo[pid];
        UserInfo storage user = userInfo[pid][msg.sender];
        if (user.quantity > 0) {
            mint(pid);
            // The reward held by the user in this pool
            uint256 userReward = pool.allocMdxAmount.mul(user.quantity).div(pool.quantity);
            pool.quantity = pool.quantity.sub(user.quantity);
            pool.allocMdxAmount = pool.allocMdxAmount.sub(userReward);
            user.quantity = 0;
            user.blockNumber = block.number;
            userSub = userSub.add(userReward);
        }
    }
    if (userSub <= 0) {
        return;
    }
    console.log(userSub);
    babyToken.transfer(msg.sender, userSub);
}
```

Our analysis shows that the given SwapMining contract may be exploited by flashloans. Speciﬁcally, a bad actor could accumulate the user.quantity by making a flashloans of swapping token A to token B. After taking the rewards from the takerWithdraw() routine, the bad actor could take a reversed swap and make proﬁts again. The bad actor could repeat the above steps to make proﬁts as long as the value of the reward is larger than swap fees.

```solidity
swapMining only router
function swap(address account, address input, address output, uint256 amount)
public
onlyRouter
returns (bool) {
    require(account != address(0), "SwapMining: taker swap account is the zero address");
    require(input != address(0), "SwapMining: taker swap input is the zero address");
    require(output != address(0), "SwapMining: taker swap output is the zero address");
    if (poolLength() <= 0)
        return false;
    if (!isWhitelist(input) || !isWhitelist(output))
        return false;
    address pair = BabyLibrary.pairFor(address(factory), input, output);
    PoolInfo storage pool = poolInfo[pairOfPid[pair]];
    // If it does not exist or the allocPoint is 0 then return
    if (pool.pair != pair || pool.allocPoint <= 0)
        return false;
    uint256 quantity = getQuantity(output, amount, targetToken);
    if (quantity <= 0)
        return false;
    mint(pairOfPid[pair]);
    pool.quantity = pool.quantity.add(quantity);
    pool.totalQuantity = pool.totalQuantity.add(quantity);
    UserInfo storage user = userInfo[pairOfPid[pair]][account];
    user.quantity = user.quantity.add(quantity);
    user.blockNumber = block.number;
    return true;
}
```

## Recommendation
Develop an eﬀective mitigation to the above sandwich attack to ensure the proper computation and dissemination of swapMining reward.
