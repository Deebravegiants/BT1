# [H] Anyone who is approving BlueprintV5 can have their funds drained

## Summary
Severity: High
Contest weight: 0.6106
Dataset id: 2668
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
payWithERC20 is supposed to be used inside BlueprintV5 contract to handle payment. But this function also can be used to drain anyone who is interact with BlueprintV5 and using it to approve payment token when creating an agent.
Payment.sol#L25-L32
```solidity
function payWithERC20(address erc20TokenAddress, uint256 amount, address fromAddress, address toAddress) public {
    // check from and to address
    require(fromAddress != toAddress, "Cannot transfer to self address");
    require(toAddress != address(0), "Invalid to address");
    require(amount > 0, "Amount must be greater than 0");
    IERC20 token = IERC20(erc20TokenAddress);
    token.safeTransferFrom(fromAddress, toAddress, amount);
}
```
the root cause simply because this function is public function, meaning anyone can call this and supply valid token address, then fill fromAddress with any address that still have allowance/approving the payment token to be spend by BlueprintV5 contract
Internal Pre-conditions
1. admin enable usdc or any erc20 token as payment by calling Blueprint::addPaymentAddress
External Pre-conditions
1. victim approve the spending of usdc or any erc20 token set in last step for BlueprintV5 contract address proxy
2. the amount approved should be greater than the amount used for creating agent with token cost
3. victim call the function to create agent (optional)
Attack Path
1. attacker call payWithERC20 supplying the parameter with usdc address, victim address and sufficient amount to be sent into attacker address
user/victim who interacted would lose their funds drained by attacker

## Recommendation
make the Payment::payWithERC20 internal
