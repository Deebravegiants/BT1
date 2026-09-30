# [M] `ArcadeTreasury.sol` allowance may be overriden

## Summary
Severity: Medium
Contest weight: 0.6273
Dataset id: 18905
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an ERC20 allowance overwrite flaw that occurs because the contract calls IERC20(token).approve(spender, amount) each time an approval is needed. The approve function sets the spender's allowance to the exact amount supplied, replacing any previously granted allowance instead of adding to it. This design choice is the root cause: the internal _approve helper does not read the current allowance before calling approve, and the public gscApprove function also invokes approve with the raw amount. As a result, when multiple approval functions such as approveSmallSpend, approveMediumSpend or approveLargeSpend target the same spender, the last call silently overwrites the earlier allowance. An attacker who controls the GSC_CORE_VOTING_ROLE can exploit this by first granting a large allowance to a spender and then issuing a subsequent approval with a tiny amount (for example 1 wei), which reduces the spender's effective allowance to that tiny value. The impact is that legitimate spenders may find their allowance unexpectedly reduced, causing token transfers to fail with “transfer amount exceeds allowance” errors, or they may be unable to spend any funds at all. From the user’s perspective the UI may still show that an approval transaction succeeded, but the allowance displayed later is zero or far lower than expected, leading to confusion and potential denial‑of‑service for the protocol’s treasury operations. The condition under which this occurs is any sequence of approval calls that target the same spender without using an additive allowance pattern. The affected parties include the treasury contract, any external contracts or users that rely on the allowance to move tokens, and the protocol’s governance participants who expect consistent spending limits. The issue was discovered during a Code4rena audit when the reviewers noticed the direct use of approve and the lack of accumulation logic. It can be hard to notice because approve does not revert on overwrite and the contract emits no warning; the only symptom is a changed allowance value that may only be observed later when a transfer fails. The bug belongs to the class of ERC20 allowance overwrite or race‑condition vulnerabilities, where cumulative allowances are incorrectly handled. To remediate, the contract should read the existing allowance and approve the sum of the old allowance and the new amount, or use the ERC20 increaseAllowance function, thereby ensuring that each approval adds to the previous allowance instead of replacing it. This change restores the intended accounting guarantees and prevents accidental or malicious reduction of spend limits.

## Proof of Concept
In the `gscApprove()` method, it is possible to give `spender` a certain allowance.

The code is as follows:

```solidity
function gscApprove(
    address token,
    address spender,
    uint256 amount
) external onlyRole(GSC_CORE_VOTING_ROLE) nonReentrant {
    if (spender == address(0)) revert T_ZeroAddress("spender");
    if (amount == 0) revert T_ZeroAmount();

    // Will underflow if amount is greater than remaining allowance
    gscAllowance[token] -= amount;

    _approve(token, spender, amount, spendThresholds[token].small);
} 

function _approve(address token, address spender, uint256 amount, uint256 limit) internal {
    // check that after processing this we will not have spent more than the block limit
    uint256 spentThisBlock = blockExpenditure[block.number];
    if (amount + spentThisBlock > limit) revert T_BlockSpendLimit();
    blockExpenditure[block.number] = amount + spentThisBlock;

    // approve tokens
    IERC20(token).approve(spender, amount);

    emit TreasuryApproval(token, spender, amount);
}    
```

From the above code, we can see that when executed, `gscApprove` consumes `gscAllowance[]` and ultimately uses `IERC20(token).approve();` to give the `spender` allowance. Since the direct use is `IERC20.approve(spender, amount)`, the amount of the allowance is overwritten, whichever comes last.

In the other methods, `approveSmallSpend`, `approveMediumSpend` and `approveLargeSpend` also use `IERC20(token).approve();`, which causes them to override each other if targeting the same `spender`.

Even if there is a malicious `GSC_CORE_VOTING_ROLE`, it is possible to execute `gscApprove(amount=1 wei)` after `approveLargeSpend()` to reset to an allowance of only `1 wei`.

The recommendation is to use accumulation to avoid, intentionally or unintentionally, overwriting each other.

## Recommendation
```solidity
function _approve(address token, address spender, uint256 amount, uint256 limit) internal {
    // check that after processing this we will not have spent more than the block limit
    uint256 spentThisBlock = blockExpenditure[block.number];
    if (amount + spentThisBlock > limit) revert T_BlockSpendLimit();
    blockExpenditure[block.number] = amount + spentThisBlock;

    // approve tokens
    uint256 old = IERC20(token).allowance(address(this),spender);
    IERC20(token).approve(spender, old + amount);

    emit TreasuryApproval(token, spender, amount);
}
```
