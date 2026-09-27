# [M] 7.1 Multicall Actions During Pauses

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Corrected

During a liquidation, the liquidator can call CreditFacade._multicall. When this happens, the
ownership of the credit account is temporarily passed to the CreditFacade to allow it to properly
interact with the adapters. By using this feature, liquidators can swap tokens of the credit account to the
underlying and, thus, they don't have to supply the underlying by themselves. This is a useful feature for
any liquidator, even for the emergency ones. During pauses, however, the functionality of the credit
manager is limited. One of the limitations is that CreditManager.transferAccountOwnership fails.
This means that the liquidators cannot make any calls to the adapters.

Code corrected:

The CreditManager now allows multiple calls to be made while the system is paused as long as the
call is related to an emergency liquidation (whenNotPausedOrEmergency).
