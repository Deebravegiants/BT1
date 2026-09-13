# [M] 6.9 Reentrancy Into executeOp()

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Corrected

Function executeOp() can be reentered. At this time OperationStorage may be in an inconsistent state,
amongst others (actions), returnValues may contain values.

While this is not an intended use case, technically the possibility exists. To reduce risks, this may be
restricted especially as the execution reaches untrusted third-party code (integrations, token contracts).

Furthermore note that after a takeAFlashloan action, the OperationExecutor temporarily has the right
to call execute() on the DsProxy of the user. OperationExecutor.onFlashloan() uses this to
execute aggregate() on the initiator.

Currently this is not exploitable due to:


- The DAI Flash Mint Module features a reentrancy protection, hence no second flashloan is currently
    possible. Note that this is no requirement for an ERC3165 compliant flashloan provider, an arbitrary
    flashloan proivder may not, e.g., the reference implementation of ERC3165 does not feature such a
    protection.
- ERC3165 requires the initiator being the msg.sender initiating the flashloan. It's not possible
    for an attacker to get the initiator to be the DsProxy where the OperationExecutor holds the privilege.

In the Version 1 reentrancy is also possible with aggregate(), please consider issue Visibility of
aggregate function.

Code corrected:

The updated code prevents reentrancy into executeOp() by leveraging the OperationStorage contract:
The reentrancy lock is set in the OperationStorage at the beginning of the execution and released after
the operation.

Releasing can only be done by the account which set the reentrancy lock; releasing the lock sets the
stored account to 0x0. This ensures that the original call to executeOp() reverts in case of reentrancy.
