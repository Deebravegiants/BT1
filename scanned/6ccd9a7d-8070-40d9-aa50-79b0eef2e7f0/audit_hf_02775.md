# [M] Block Order Filling For Tokens That Prevent Nonzero Allowances Modifications

## Summary
Severity: Medium
Contest weight: 0.5956
Dataset id: 15169
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When the function SolverNetExecutor.approve() is invoked within the SolverNetOutbox.withExpenses() modifier, it
is expected to grant a nonzero allowance to the specified spender if expenses are requested by the owner of the order.
However, certain tokens, such as USDT, require that an existing allowance be explicitly set to zero before approving a
new nonzero amount. This requirement is not accounted for in the current implementation.
Below is the approve() function from USDT, demonstrating this constraint:
```solidity
function approve(address _spender, uint _value) public onlyPayloadSize(2 * 32) {
    // To change the approve amount you first have to reduce the address’
    // allowance to zero by calling `approve(_spender, 0)` if it is not
    // already 0, to mitigate the race condition described here:
    // https://github.com/ethereum/EIPs/issues/20#issuecomment-263524729
    require(!((_value != 0) && (allowed[msg.sender][_spender] != 0)));
    allowed[msg.sender][_spender] = _value;
    Approval(msg.sender, _spender, _value);
}
```
Attack Vector:
1. An attacker identifies that a user intends to open an order involving USDT on the destination chain, meaning that
SolverNetExecutor will approve a nonzero allowance to the user for USDT.
2. The attacker submits an order that manipulates SolverNetExecutor to set a nonzero allowance for the user. This
is achieved by crafting orderData.calls so that SolverNetExecutor executes USDT.approve(user, 1):
```solidity
struct Call {
    address target;
    // USDT contract address
    bytes4 selector; // approve(address,uint256) function selector
    uint256 value;
    // 0 (ETH transfer value)
    bytes params;
    // Encoded parameters: user as spender, 1 USDT as amount
}
SolverNet.Call[] memory calls = orderData.calls;
if (calls.length == 0) revert InvalidMissingCalls();
for (uint256 i; i < calls.length; ++i) {
    SolverNet.Call memory call = calls[i];
    if (call.target == address(0)) revert InvalidCallTarget();
}
```
3. When the attacker's order is executed on the destination chain, it sets the USDT allowance of SolverNetExecutor
to 1 for the user:
Omni SolverNet
```solidity
_executor.execute{ value: call.value }(
    call.target, call.value, abi.encodePacked(call.selector, call.params)
)
```
4. Later, when the solver attempts to fill the user's order on the destination chain, the modifier withExpenses tries
to approve a new nonzero amount from SolverNetExecutor for the user. However, since the current allowance
is already nonzero, the approval fails and reverts, preventing the user's order from being fulfilled:
```solidity
if (spender != address(0)) _executor.approve(token, spender, amount);
function approve(address token, address spender, uint256 amount) external onlyOutbox {
    token.safeApprove(spender, amount);
}
```

## Recommendation
To mitigate this issue, it is advised to use SafeTransferLib.safeApproveWithRetry() instead of approve(). This func-
tion ensures that if a token does not allow changing allowances from a nonzero value, it first resets the allowance to
zero before setting the new value.
