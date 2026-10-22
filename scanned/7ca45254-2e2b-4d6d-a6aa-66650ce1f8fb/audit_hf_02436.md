# [M] Possible Costly yVault LPs From Improper Liquidity Initialization

## Summary
Severity: Medium
Contest weight: 0.4627
Dataset id: 13082
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Stone protocol allows users to deposit supported assets and get in return st-wrapped tokens to represent the pool share. While examining the share calculation with the given deposits, we notice an issue that may unnecessarily make the pool token, i.e., stUSDC, extremely expensive and bring hurdles (or even causes loss) for later depositors. To elaborate, we show below the deposit() routine. This routine is used for participating users to deposit the supported assets (e.g., USDC) and get respective stUSDC pool tokens in return. The issue occurs when the pool is being initialized under the assumption that the current pool is empty.

```solidity
function deposit(uint256 _amount) public {
    uint256 _pool = balance();
    uint256 _before = token.balanceOf(address(this));
    token.safeTransferFrom(msg.sender, address(this), _amount);
    uint256 _after = token.balanceOf(address(this));
    _amount = _after.sub(_before);
    // Additional check for deflationary tokens
    uint256 shares = 0;
    if (totalSupply() == 0)
        shares = _amount;
    else
        shares = (_amount.mul(totalSupply())).div(_pool);
    _mint(msg.sender, shares);
}
```

Specifically, when the pool is being initialized (line 81), the share value directly takes the value of amount (line 82), which is manipulatable by the malicious actor. As this is the first deposit, the current total supply equals the calculated shares = _amount = 1 WEI. With that, the actor can further deposit a huge amount of USDC assets with the goal of making the stUSDC pool token extremely expensive. An extremely expensive stUSDC pool token can be very inconvenient to use as a small number of 1_WEI may denote a large value. Furthermore, it can lead to precision issue in truncating the computed pool tokens for deposited assets. If truncated to be zero, the deposited assets are essentially considered dust and kept by the pool without returning any pool tokens. This is a known issue that has been mitigated in popular Uniswap. When providing the initial liquidity to the contract (i.e. when totalSupply is 0), the liquidity provider must sacrifice 1000 LP tokens (by sending them to address(0)). By doing so, we can ensure the granularity of the LP tokens is always at least 1000 and the malicious actor is not the sole holder. This approach may bring an additional cost for the initial liquidity provider, but this cost is expected to be low and acceptable.

## Recommendation
Revise current execution logic of deposit() to defensively calculate the share amount when the pool is being initialized. An alternative solution is to ensure guarded launch that safeguards the first deposit to avoid being manipulated.
