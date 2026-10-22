# [M] Possible Costly LPs From Improper vTHOR Initialization

## Summary
Severity: Medium
Contest weight: 0.4629
Dataset id: 13267
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vTHOR contract allows the users to stake their funds to receive vTHOR token as shares. The staking users will get their pro-rata share based on their staked amount. While examining the share calculation with the given deposits, we notice an issue that may unnecessarily make the share extremely expensive and bring hurdles (or even causes loss) for later depositors. To elaborate, we show below the deposit() routine. This deposit() routine is used for participating users to deposit the supported asset (e.g., token) and get respective shares in return. The issue occurs when the vTHOR contract is being initialized under the assumption that the current contract is empty.

```solidity
function deposit(uint256 amount) public {
    uint256 totalShares = totalSupply;
    uint256 totalDeposits = IERC20(token).balanceOf(address(this));
    token.safeTransferFrom(msg.sender, address(this), amount);
    if (totalShares == 0 || totalDeposits == 0) {
        _mint(msg.sender, amount);
    } else {
        _mint(msg.sender, (amount * totalShares) / totalDeposits);
    }
}
```

Specifically, when the contract is being initialized, the share value directly takes the value of amount (line 22), which is manipulatable by the malicious actor. As this is the first deposit, the current total supply equals the calculated shares = 1 WEI. With that, the actor can further deposit a huge amount of token with the goal of making the share extremely expensive. An extremely expensive share can be very inconvenient to use as a small number of 1 Wei may denote a large value. Furthermore, it can lead to precision issue in truncating the computed pool tokens for deposited assets. If truncated to be zero, the deposited assets are essentially considered dust and kept by the pool without returning any pool tokens. This is a known issue that has been mitigated in popular Uniswap. When providing the initial liquidity to the contract (i.e. when totalSupply is 0), the liquidity provider must sacrifice 1000 LP tokens (by sending them to address(0)). By doing so, we can ensure the granularity of the LP tokens is always at least 1000 and the malicious actor is not the sole holder. This approach may bring an additional cost for the initial liquidity provider, but this cost is expected to be low and acceptable.

## Recommendation
Revise current execution logic of share calculation to defensively calculate the share amount when the pool is being initialized. An alternative solution is to ensure guarded launch that safeguards the first deposit to avoid being manipulated.
