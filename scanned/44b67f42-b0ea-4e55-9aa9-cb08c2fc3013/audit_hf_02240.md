# [M] Possible Costly LPs From Improper Bank Initialization

## Summary
Severity: Medium
Contest weight: 0.4604
Dataset id: 12351
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the Kalmar protocol, the Bank contract is an essential one that manages current debt positions and mediates the access to various workers (or Goblins). Meanwhile, the Bank contract allows liquidity providers to provide liquidity so that lenders can earn high interest and the lending interest rate comes from leveraged yield farmers. While examining the share calculation when lenders provide liquidity (via deposit()), we notice an issue that may unnecessarily make the Bank-related pool token extremely expensive and bring hurdles (or even causes loss) for later liquidity providers.
To elaborate, we show below the deposit() routine. This routine is used for liquidity providers to deposit desired liquidity and get respective pool tokens in return. The issue occurs when the pool is being initialized under the assumption that the current pool is empty.
```solidity
/// @dev Add more ETH to the bank. Hope to get some good returns.
function deposit() external payable accrue(msg.value) nonReentrant {
    uint256 total = totalETH().sub(msg.value);
    uint256 share = total == 0 ? msg.value : msg.value.mul(totalSupply()).div(total);
    _mint(msg.sender, share);
}

/// @dev Withdraw ETH from the bank by burning the share tokens.
function withdraw(uint256 share) external accrue(0) nonReentrant {
    uint256 amount = share.mul(totalETH()).div(totalSupply());
    _burn(msg.sender, share);
    SafeToken.safeTransferETH(msg.sender, amount);
}
```
Public
Specifically, when the pool is being initialized, the share value directly takes the given value of msg.value (line 106), which is under control by the malicious actor. As this is the first deposit, the current total supply equals the calculated share = total == 0 ? msg.value : msg.value.mul(totalSupply()).div(total) = 1WEI. After that, the actor can further transfer a huge amount of tokens with the goal of making the pool token extremely expensive.
An extremely expensive pool token can be very inconvenient to use as a small number of 1WEI may denote a large value. Furthermore, it can lead to precision issue in truncating the computed pool tokens for deposited assets. If truncated to be zero, the deposited assets are essentially considered dust and kept by the pool without returning any pool tokens.
This is a known issue that has been mitigated in popular UniswapV2. When providing the initial liquidity to the contract (i.e. when totalSupply is 0), the liquidity provider must sacrifice 1000 LP tokens (by sending them to address(0)). By doing so, we can ensure the granularity of the LP tokens is always at least 1000 and the malicious actor is not the sole holder. This approach may bring an additional cost for the initial stake provider, but this cost is expected to be low and acceptable.
Another alternative requires a guarded launch to ensure the pool is always initialized properly.

## Recommendation
Revise current execution logic of deposit() to defensively calculate the share amount when the pool is being initialized.
