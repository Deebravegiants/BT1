# [H] Critical DOS in queue processing if asynccancellations are allowed

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23287
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Description: The cancelRedeemRequest() function can be used to DOS the queue processing (ie. processUp-
ToShares() and processUpToRequestID() can be made to revert).
This is the attack path :
• cancelRedeemRequest() marks state.pendingCancelRedeemRequest = true;
• Assume that this cancellation is not instantly fulfilled, as the associated strategy may support async cancel-
lations
```solidity
function cancelRedeemRequest(uint256 requestId, address controller) public onlyAuth {
    _checkController(controller);
    VaultState storage state = _vaultStates[controller];
    if (state.pendingRedeemRequest == 0) revert NoPendingRedeemRequest();
    if (state.pendingCancelRedeemRequest) revert CancelRedeemRequestPending();
    state.pendingCancelRedeemRequest = true;
    bool canCancel = strategy.onCancelRedeemRequest(address(this), controller); // @audit strategy
    // can choose to return false here, thus mandating async cancellations.
    if (canCancel) {
        uint256 pendingShares = state.pendingRedeemRequest;
        _fulfillCancelRedeemRequest(uint128(requestId), controller);
        _reduce(controller, pendingShares);
    }
    emit CancelRedeemRequest(controller, requestId, msg.sender);
}
```
• At this step, it also skips "reducing" the shares in request state, as _reduce() will only be called when cancel-
lation is fulfilled via fulfillCancelRedeemRequest()
• Later when processUpToShares() is called, _processRequest() returns normal request data (does not re-
turn "zero values" as request.shares was not reduced in the cancel logic ) => so it doesn't break the loop or
continue with nextRequestID
• It goes on to call _fulfillRedeemRequest(), where it reverts due to pendingCancelRedeemRequest = true
```solidity
function _fulfillRedeemRequest(uint128 requestId, address controller, uint256 shares, uint256 price)
    internal
    override
{
    VaultState storage state = _vaultStates[controller];
    if (state.pendingRedeemRequest == 0) revert NoRedeemRequest();
    if (state.pendingRedeemRequest < shares) revert InsufficientAmount();
    if (state.pendingCancelRedeemRequest) revert RedeemRequestWasCancelled(); // @audit
    // ...
}
```
This means even a single async cancellation (that is pending for processing) can DOS queue processing.
Impact: Queue processing can be repeatedly DOS'ed under normal operations as well as by an attacker frontrun-
ning a process call, in case the strategy contract allows async cancellations.

## Recommendation
Consider removing async cancellations' support from the system, which prevents this kind of attacks.
