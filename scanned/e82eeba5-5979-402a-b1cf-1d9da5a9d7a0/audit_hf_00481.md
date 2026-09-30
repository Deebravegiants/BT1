# [H] attacker can drain StopLimit con-

## Summary
Severity: High
Contest weight: 0.7869
Dataset id: 1922
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
performUpkeep::StopLimit function increases allowance of input token for Bracket contract.
https://github.com/oku/oku/blob/ee3f781a73d65e33fb452c9a44eb1337c5cfdbd6/oku-custom-order-types/contracts/automatedTrigger/StopLimit.sol#L100-L104
updateApproval(
    address(BRACKET_CONTRACT),
    order.tokenIn,
    order.amountIn
);
https://github.com/oku/oku-custom-order-types/contracts/automatedTrigger/StopLimit.sol#L397-L411
```solidity
function updateApproval(
    address spender,
    IERC20 token,
    uint256 amount
) internal {
    // get current allowance
    uint256 currentAllowance = token.allowance(address(this), spender);
    if (currentAllowance < amount) {
        // amount is a delta, so need to pass max - current to avoid overflow
        token.safeIncreaseAllowance(
            spender,
            type(uint256).max - currentAllowance
        );
    }
}
```
So now Bracket contract can transfer input tokens to itself in fillStopLimitOrder function.
https://github.com/oku/oku-custom-order-types/contracts/automatedTrigger/StopLimit.sol#L126-L140
```solidity
BRACKET_CONTRACT.fillStopLimitOrder(
    swapPayload,
    order.takeProfit,
    order.stopPrice,
    order.amountIn,
    order.orderId,
    tokenIn,
    tokenOut,
    order.recipient,
    order.feeBips,
    order.takeProfitSlippage,
    order.stopSlippage,
    false, //permit
    "0x" //permitPayload
);
```
https://github.com/oku/oku-custom-order-types/contracts/automatedTrigger/Bracket.sol#L147-L165
```solidity
function fillStopLimitOrder(
    bytes calldata swapPayload,
    uint256 takeProfit,
    uint256 stopPrice,
    uint256 amountIn,
    uint96 existingOrderId,
    IERC20 tokenIn,
    IERC20 tokenOut,
    address recipient,
    uint16 existingFeeBips,
    uint16 takeProfitSlippage,
    uint16 stopSlippage,
    bool permit,
    bytes calldata permitPayload
) external override nonReentrant {
    require(
        msg.sender == address(MASTER.STOP_LIMIT_CONTRACT()),
        "Only Stop Limit"
    );
```
https://github.com/oku/oku-custom-order-types/contracts/automatedTrigger/Bracket.sol#L336
```solidity
token.safeTransferFrom(owner, address(this), amount);
```
Now even after this transfer almost type(uint256).max allowance is there for Bracket contract. Attacker can take this as advantage and drain StopLimit contract funds.
1) Attacker checks for which tokens there is almost type(uint256).max allowance for Bracket contract to transfer tokens of StopLimit contract. (lets say for tokens A, B, C, D etc...)
2) Attacker creates a readily executable order in Bracket contract such that tokenOut = tokenA (for which Bracket contract already has almost type(uint256).max allowance to transfer StopLimit contract's tokenA tokens). 
3) Then attacker calls: performUpkeep::Bracket with respect to this order, with target = address of tokenA, txData such that it calls transferFrom with from = address of StopLimit contract, to = address of Bracket contract, value = number of tokenA tokens StopLimit contract has (or something closer to it). And he sets feeBips = 0.
4) performUpkeep function internally calls execute function
https://github.com/oku/oku-custom-order-types/contracts/automatedTrigger/Bracket.sol#L85-L101
```solidity
function performUpkeep(
    bytes calldata performData
) external override nonReentrant {
    MasterUpkeepData memory data = abi.decode(
        performData,
        (MasterUpkeepData)
    );
    Order memory order = orders[pendingOrderIds[data.pendingOrderIdx]];
    require(
        order.orderId == pendingOrderIds[data.pendingOrderIdx],
        "Order Fill Mismatch"
    );
    // deduce if we are filling stop or take profit
    (bool inRange, bool takeProfit, ) = checkInRange(order);
    require(inRange, "order ! in range");
```
https://github.com/oku/oku-custom-order-types/contracts/automatedTrigger/Bracket.sol#L108-L115
```solidity
(uint256 swapAmountOut, uint256 tokenInRefund) = execute(
    data.target,
    data.txData,
    order.amountIn,
    order.tokenIn,
    order.tokenOut,
    bips
);
```
https://github.com/oku/oku-custom-order-types/contracts/automatedTrigger/Bracket.sol#L526-L568
```solidity
function execute(
    address target,
    bytes memory txData,
    uint256 amountIn,
    IERC20 tokenIn,
    IERC20 tokenOut,
    uint16 bips
) internal returns (uint256 swapAmountOut, uint256 tokenInRefund) {
    // update accounting
    uint256 initialTokenIn = tokenIn.balanceOf(address(this));
    uint256 initialTokenOut = tokenOut.balanceOf(address(this));
    // approve
    tokenIn.safeApprove(target, amountIn);
    // perform the call
    (bool success, bytes memory result) = target.call(txData);
    if (success) {
        uint256 finalTokenIn = tokenIn.balanceOf(address(this));
        require(finalTokenIn >= initialTokenIn - amountIn, "over spend");
        uint256 finalTokenOut = tokenOut.balanceOf(address(this));
        // if success, we expect tokenIn balance to decrease by amountIn
        // and tokenOut balance to increase by at least minAmountReceived
        require(
            finalTokenOut - initialTokenOut >
            MASTER.getMinAmountReceived(
                amountIn,
                tokenIn,
                tokenOut,
                bips
            ),
            "Too Little Received"
        );
        swapAmountOut = finalTokenOut - initialTokenOut;
        tokenInRefund = amountIn - (initialTokenIn - finalTokenIn);
    } else {
        // force revert
        revert TransactionFailed(result);
    }
}
```
In execute function after the external call to target (tokenA), tokenOut balance of contract increases by amount used as value in call (which is almost equal to available balance of StopLimit contract for tokenA). So finalTokenOut - initialTokenOut = value. So following require check is passed:
```solidity
require(
    finalTokenOut - initialTokenOut >
    MASTER.getMinAmountReceived(
        amountIn,
        tokenIn,
        tokenOut,
        bips
    ),
    "Too Little Received"
);
```
And also
```solidity
require(finalTokenIn >= initialTokenIn - amountIn, "over spend");
```
This check passes as we are not transferring any TokenIn tokens. So now swapAmountOut = finalTokenOut - initialTokenOut; swapAmountOut = value. (value used in external call to tokenA). Now this swapAmountOut will be transferred to recipient address (set by attacker).
https://github.com/oku/oku-custom-order-types/contracts/automatedTrigger/Bracket.sol#L135
```solidity
order.tokenOut.safeTransfer(order.recipient, adjustedAmount);
```
Here adjustedAmount = swapAmountOut = value. (as we set feeBips = 0).
https://github.com/oku/oku-custom-order-types/contracts/automatedTrigger/Bracket.sol#L125-L128
```solidity
(uint256 feeAmount, uint256 adjustedAmount) = applyFee(
    swapAmountOut,
    order.feeBips
);
```
So finally through this process attacker can drain all funds of StopLimit contract by creating orders in Bracket contract with tokenOut set to tokens for which Bracket contract has allowance to transfer from StopLimit contract, setting takeProfit and stopPrice so that order is readily executable, and setting target to these tokenOut tokens and txData such that it calls transferFrom function with from = address of StopLimit contract, to = address of Bracket contract, and value = available balance of tokenOut tokens for StopLimit contract respectively.

## Recommendation
StopLimit contract should increase allowance of Bracket contract to transfer tokens only which are required in fillStopLimitOrder function (not to type(uint256).max).
