# [M] vePeg#_delegate perpetualLocked requirement can easily be bypassed

## Summary
Severity: Medium
Contest weight: 0.3984
Dataset id: 2744
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function _delegate(uint256 _from, uint256 _to) internal {
    LockedBalance memory currentLock = locked[_from];

    require(currentLock.perpetuallyLocked == true, "Lock is not perpetual");

    address delegator = ownerOf(_from);
    address delegatee = _to == 0 ? address(0) : ownerOf(_to);

    address currentDelegate = delegates(delegator);

    _delegates[delegator] = delegatee;

    _moveAllDelegates(delegator, currentDelegate, delegatee);
}
```

We see above that when delegating a token, it is required the from token is perpetually locked. However we see in the lines below that all tokens from the delegator are moved. As a result, all tokens perpetual or not are delegated to the new delegatee. This makes the perpetual check useless as even a small perpetual lock can be used to bypass this check for all tokens.

## Recommendation
The methodology for delegation should be carefully considered and redesigned.
