# [C] Unnecessary Reentrancy Protection In markFilled() Function Allows Fund Theft

## Summary
Severity: Critical
Contest weight: 0.7870
Dataset id: 15176
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The function markFilled() is used to mark an order as filled on the source chain after it has been executed on the
destination chain. Although this function uses the nonReentrant modifier to protect against reentrancy attacks, its use
in this function could allow a malicious user to steal funds.
```solidity
function markFilled(bytes32 id, bytes32 fillHash, address creditedTo) external xrecv nonReentrant
```
Here's how the attack can unfold:
1. The Setup: The attacker opens an order, which we will call orderA, and it is executed on the destination chain,
meaning the attacker receives the necessary tokens on the destination chain. Afterwards, the Solver sends a
cross-rollup message via Omni Core to confirm that orderA has been fulfilled on the source chain.
2. The Attack Begins: While the transaction is pending, the attacker notices the transaction in the mempool that is
going to call OmniPortal.xsubmit(). Before this transaction is executed on the source chain, the attacker triggers
an attack in one of the following two ways:
1a. The attacker calls open() with a malicious token that they control (a fake token). When processing the de-
posit, this malicious token will be used, allowing the attacker to hijack the control flow during deposit processing.
```solidity
function _processDeposit(SolverNet.Deposit memory deposit) internal {
    if (deposit.token == address(0)) {
        if (msg.value != deposit.amount) revert InvalidNativeDeposit();
    } else {
        deposit.token.safeTransferFrom(msg.sender, address(this), deposit.amount);
    }
}
```
1b.
Alternatively, the attacker can call
close() using an old order that was not filled before, and whose
fillDeadline + CLOSE_BUFFER has passed. This allows the attacker to close the order and hijack the control
flow during deposit transfer.
```solidity
function _transferDeposit(bytes32 id, address to) internal {
    SolverNet.Deposit memory deposit = _orderDeposit[id];
    if (deposit.amount > 0) {
        if (deposit.token == address(0)) to.safeTransferETH(deposit.amount);
        else deposit.token.safeTransfer(to, deposit.amount);
    }
}
```
3. Execution of the Attack: Now that the attacker has control, they call OmniPortal.submit() to execute the trans-
action that was pending in the mempool, which is supposed to mark orderA as filled.
4. Reentrancy Check Triggers a Revert: When
OmniPortal.xsubmit() is executed, it calls the internal function
OmniPortal._exec(), which in turn calls SolverNetInbox.markFilled(). However, because of the nonReentrant
modifier in markFilled(), the transaction fails as the attacker already entered the protocol in steps 1a or 1b.
Omni SolverNet
5. Message Loss: Due to the design of the OmniPortal, the failure does not cause a revert in OmniPortal.xsubmit().
This means that even though the transaction to mark orderA as filled fails on the source chain, it is assumed to
have been executed and cannot be retried.
6. Completion of the Attack: After this failure, control is handed back to the SolverNetInbox, where the transaction
from step 1a or 1b continues.
Now that the transaction has ended, the attacker has already received the tokens for orderA on the destination chain,
but the transaction that would mark it as filled on the source chain has failed and cannot be retried. In other words, the
protocol assumes that orderA is not filled on the destination chain yet. After waiting for fillDeadline + CLOSE_BUFFER,
the attacker can call close() to retrieve their deposit from the source chain associated with orderA. This allows the
attacker to steal funds by receiving the deposit on the source chain during closing the order as well as receiving the
tokens on the destination chain during filling the order.
The main issue here is the inappropriate use of the nonReentrant modifier without valid justification. The nonReentrant
check in markFilled() causes the transaction to fail under these conditions, allowing the attacker to exploit the sys-
tem.

## Recommendation
A possible solution is to remove the nonReentrant check from the markFilled() function, ensuring that it does not
block valid transactions and preventing this type of attack.
