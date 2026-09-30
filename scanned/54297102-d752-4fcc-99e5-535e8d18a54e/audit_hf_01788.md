# [M] Potential race condition between repayments and liquidations due to missing queue check, may allow incorrect accounting

## Summary
Severity: Medium
Contest weight: 0.2318
Dataset id: 9811
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The LiquidOps protocol has a potential race condition between loan repayments and liquidations that can lead to accounting inconsistencies. The issue exists because the repay.handler function does not check if the user is in the controller's LiquidationQueue before processing a repayment. While the initial transfer handler is wrapped with queue.useQueue() which performs queue checks, the internal repay.handler that processes the Credit-Notice with X-Action = "Repay" lacks this protection: Handlers.advanced({ name = "borrow-repay", pattern = { From = CollateralID, Action = "Credit-Notice", ["X-Action"] = "Repay" }, handle = repay.handler, errorHandler = repay.error }) In the repay.handler function, no queue check is performed: function repay.handler(msg) assert( assertions.isTokenQuantity(msg.Tags.Quantity), "Invalid incoming transfer quantity" ) -- quantity of tokens supplied local quantity = bint(msg.Tags.Quantity) -- allow repaying on behalf of someone else local target = msg.Tags["X-On-Behalf"] or msg.Tags.Sender -- check if a loan can be repaid for the target assert( repay.canRepay(target, msg.Timestamp), "Cannot repay a loan for this user" ) -- execute repay local refundQty, actualRepaidQty = repay.repayToPool( target, quantity, true ) -- Rest of the function... } Meanwhile, the controller's liquidation process adds users to the LiquidationQueue during liquidation: -- Add the target to the liquidation queue to lock further liquidations table.insert(LiquidationQueue, target) -- ... liquidation processing ... -- Remove target from liquidation queue after completion LiquidationQueue = utils.filter( function (v) return v ~= target end, LiquidationQueue ) Impact: This race condition can lead to a an incorrect accounting scenario where both repayment and liquidation succeed simultaneously and is as follows:

## Recommendation
Apply queue checks to all handlers that modify user positions, including the internal repay.handler.
