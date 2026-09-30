# [M] Swap execution can completely fail in some cases when tokens like BNB are involved

## Summary
Severity: Medium
Contest weight: 0.4353
Dataset id: 5145
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
swapExactInputMultiple() is supposed to handle a batch of swap operations, all leading to WNATIVE which can then be unwrapped and bridged as ETH / native token. Current protocol logic has means to handle the whole swap transaction in case any of the constituent swap operation fails, which allows the remaining transaction to go through normally.
This is done by wrapping the swap call to the router in a try-catch block, with the catch block handling token approval reset and refunds. But this catch block does not work correctly for some ERC20 tokens like BNB on Ethereum:
```solidity
catch {
    // If the swap fails, decrease the allowance of the permit2 contract.
    token.safeDecreaseAllowance(address(permit2), amountIn);
    // Return the tokens to the sender.
    token.safeTransfer(msg.sender, amountIn);
    emit BurnerEvents.SwapFailed(msg.sender, param.tokenIn, amountIn, "Router error");
    unchecked { ++i; }
    continue;
}
```
Notably, this safeDecreaseAllowance() call is from Openzeppelin's SafeERC20 library. The call flow leads to forceApprove(0), where token.approve(0) is called. The approve(0) call needs to succeed for this forceApprove() call to go through. This is exactly where tokens like BNB misbehave: they revert on an approve(0) call.
As a result, the safeDecreaseAllowance() call will fail for such tokens, with the revert bubbling up: causing the whole transaction to revert since this operation is inside a catch block.

## Recommendation
Consider wrapping this safeDecreaseAllowance() call in a try-catch block, or document that certain tokens are not supported and including them in the swaps could lead to the failure of the whole batch-swap transaction.
