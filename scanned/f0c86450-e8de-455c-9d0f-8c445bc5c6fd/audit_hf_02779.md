# [H] Inadequate Gas Estimation Leads To Fund Theft From Memory Expansion Costs

## Summary
Severity: High
Contest weight: 0.7897
Dataset id: 15177
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The function _fillGasLimit() is designed to estimate the gas required to mark an order as filled on the inbox. This
gas is needed to cover the cost of executing the _fillHash() function on the source chain:
```solidity
function _fillHash(bytes32 orderId) internal view returns (bytes32) {
    SolverNet.Header memory header = _orderHeader[orderId];
    SolverNet.Call[] memory calls = _orderCalls[orderId];
    SolverNet.TokenExpense[] memory expenses = _orderExpenses[orderId];
    SolverNet.FillOriginData memory fillOriginData = SolverNet.FillOriginData({
        srcChainId: uint64(block.chainid),
        destChainId: header.destChainId,
        fillDeadline: header.fillDeadline,
        calls: calls,
        expenses: expenses
    });
    return keccak256(abi.encode(orderId, abi.encode(fillOriginData)));
}
```
In this function, the data from
_orderCalls[orderId] is loaded from storage into memory. However, the function
_fillGasLimit() calculates the cost of loading from storage as follows:
```solidity
// 2500 gas for Call array length SLOAD + dynamic cost of reading each call.
uint256 callsGas = 2500;
for (uint256 i; i < fillData.calls.length; ++i) {
    SolverNet.Call memory call = fillData.calls[i];
    unchecked {
        // 5000 gas for the two slots that hold target, selector, and value.
        // 2500 gas per params slot (1 per function argument) used (minimum of 1 slot).
        callsGas += 5000 + (FixedPointMathLib.divUp(call.params.length + 32, 32) * 2500);
    }
}
```
This cost estimate includes the gas for loading the call array length, as well as the gas for loading each call's parameters.
However, it fails to account for memory expansion costs. For example, if the mstore opcode occupies 256 KB of
memory space, the cost for memory expansion could be around 155,648 gas. This additional gas cost is not factored
into the estimate, despite the 100k base gas being accounted for.
This creates a vulnerability. If an attacker opens an order with a parameter length that is too large, after the order is filled
on the destination chain and the attacker receives the tokens, the Solver will attempt to send a cross-rollup message via
Omni Core to confirm the fulfillment. However, due to the underestimated gas in _fillGasLimit(), the transaction
cannot be marked as filled on the source chain, as it requires more gas than expected. The function
_fillHash()
exceeds the estimated gas limit, preventing the Solver from marking the order as filled, and preventing the Solver from
claiming the deposited amount.
Omni SolverNet
After the CLOSE_BUFFER period, the attacker can close the order and receive the deposited amount, even though the
order was filled on the destination chain, leading to the theft of funds.
It is important to note that this scenario could also occur for order expenses.

## Recommendation
A potential solution is to include the cost of memory expansion in the gas estimation within _fillGasLimit(), based
on the Ethereum yellow paper:
Gmemory * (max_memory / 32) + floor(max_memory^2 / 524,288)
Alternatively, a simplified approach could be:
callsGas += 3 * (call.params.length / 32) + (call.params.length * call.params.length / 524,288)
