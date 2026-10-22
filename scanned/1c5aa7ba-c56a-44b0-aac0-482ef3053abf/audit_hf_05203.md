# [C] Partial redemption can be used to steal assets

## Summary
Severity: Critical
Contest weight: 0.0000
Dataset id: 23330
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The request state is not handled properly when redeem requests are filled partially, leading to an inflated redemption price for the remaining part of the request.  

When a new redemption is pushed onto an existing requestID, then the average redemption price is calculated using the updated totalValue and updated request.shares. This is then stored as the request.sharePrice (used for calculating assets owed for those shares).

```solidity
} else { // if controller had an existing active requestID
    requestId = requestId_;
    WithdrawalRequest storage request = _queue.requests[requestId_];
    request.shares += shares;
    if (processingMode == ProcessingMode.RequestPrice) {
        request.totalValue += shares.mulDiv(sharePrice, _precision);
        request.sharePrice = request.totalValue.mulDiv(_precision, request.shares); // the average sharePrice is being calculated here.
    } // the whole request will have a single price, averaged recursively as new redeem requests come up.
    totalQueuedShares += shares;
}
```

This works fine when request is fulfilled completely or cancelled completely as in those cases request data gets wiped out. But the problem is that when such a request is filled partially, this totalValue is never decreased while request.shares is decreased.

```solidity
function _reduce(address controller, uint256 shares) internal returns (uint256 remainingShares) {
    uint128 requestId = _requestIds[controller];
    if (requestId == 0) revert NoQueueRequest();
    uint256 currentShares = _queue.requests[requestId].shares;
    if (shares > currentShares || currentShares == 0) revert InsufficientShares();
    remainingShares = currentShares - shares;
    totalQueuedShares -= shares;
    if (remainingShares == 0) {
        _delete(controller, requestId);
    } else {
        _queue.requests[requestId].shares = remainingShares;
    } // @audit the totalValue is not updated here.
}
```

**Attack path**  

1. User places a redeem request for 100 shares at a time when sharePrice == 2. So the request data stored is => {request.totalValue = 200, request.sharePrice = 2, request.shares = 100}.  
2. This request gets fulfilled partially i.e. 50 shares. Resultant state => {request.totalValue = 200, request.sharePrice = 2, request.shares = 50}. User got 100 assets.  
3. User places another redeem request with 100 shares for the same controller address, thus the same requestID data will be modified. The new sharePrice will be calculated using an inflated "request.totalValue" and a normal request.shares. As per the calculation, the resultant state => {request.totalValue = 400, request.shares = 150, and request.sharePrice = 2.66}.  
4. Assume this request gets filled completely. User now gets 400 assets.  

User got a total of 500 assets for redeeming 200 shares, even though the sharePrice was only 2. This is because the calculation uses an inflated value of request.totalValue to calculate the redemption price.  

This request.sharePrice is used when calculating assets owed to the controller in `_fulfillRedeemRequest()` flow.  

This means an inflated amount of assets will be added to the `VaultState.maxWithdraw` ⇒ allowing controller to claim more assets than they deserved if actual sharePrice was used.  

Note: Partial redemption is possible when `fulfillRedeemRequest()` is called with a portion of the request's shares, and also possible when `processUptoShares()` is used and it hits a block with `maxShares`/`liquidityShares` (such that a particular request is not processed completely).  

Impact: An attacker can steal assets easily if their redeem request was fulfilled partially, in case the vault is configured with a `processingMode == RequestPrice`.  

This issue exists only when `processingMode == RequestPrice`, as only then the `request.sharePrice` value is used for calculating assets owed.

## Recommendation
Consider removing the processingMode logic entirely to simplify the system, or decrease redeemed assets from `request.totalValue` as part of the `_reduce()` function.
