# [M] getLoanManager.updateOfferHandler() should be executed inside confirmOfferHandler()

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-05-gondi-mitigation
Published: 2024-05-20
Source: https://github.com/code-423n4/2024-05-gondi-mitigation-findings/issues/33
Type: code-finding

## Details
# Lines of code

https://github.com/pixeldaogg/florida-contracts/blob/b83b37bbe69325b12e3b8119dfd86eb86f16fc73/src/lib/loans/LoanManagerParameterSetter.sol#L70


# Vulnerability details

## Vulnerability details
https://github.com/pixeldaogg/florida-contracts/pull/387
This PR adds that the new `__offerHandler.getMaxDuration` can't be larger than the old one, and already avoids the problem of `getMinTimeBetweenWithdrawalQueues` being too large.

Also added using `LoanManagerParameterSetter.sol` to set `offerHandler`.

In two steps:
1. setOfferHandler() => set `ProposedOfferHandler = new offerHandler`
2. after the `UPDATE_WAITING_TIME` time expires, execute `confirmOfferHandler()` to make the `ProposedOfferHandler` effective.

But currently it works immediately, not after `UPDATE_WAITING_TIME`.

```solidity
    function setOfferHandler(address __offerHandler) external onlyOwner {
        __offerHandler.checkNotZero();

        if (IPoolOfferHandler(__offerHandler).getMaxDuration() > IPoolOfferHandler(getOfferHandler).getMaxDuration()) {
            revert InvalidInputError();
        }

        getProposedOfferHandler = __offerHandler;
        getProposedOfferHandlerSetTime = block.timestamp;
@>      ILoanManager(getLoanManager).updateOfferHandler(__offerHandler); //@audit call in  confirmOfferHandler()

        emit ProposedOfferHandlerSet(__offerHandler);
    }

    /// @notice Confirm the OfferHandler contract.
    /// @param __offerHandler The new OfferHandler address.
    function confirmOfferHandler(address __offerHandler) external onlyOwner {
        if (getProposedOfferHandlerSetTime + UPDATE_WAITING_TIME > block.timestamp) {
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-05-gondi-mitigation-findings/issues/33_
