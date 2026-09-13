# [M] \[M03\] Errors and omissions in events

## Summary
Severity: Medium
Source: https://github.com/ribbon-finance/ribbon-v2/blob/3fa3bec15ad1e2b18ad87f979b87a68368497f13/contracts/vaults/base/RibbonVault.sol#L64
Type: audit-issue

## Details
Throughout the codebase, events are used to signify when changes are made to the contracts. However, many events lack indexed parameters or are missing important parameters. Some sensitive actions are lacking events altogether.

Events lacking indexed parameters include:

* The [InitiateWithdraw](https://github.com/ribbon-finance/ribbon-v2/blob/3fa3bec15ad1e2b18ad87f979b87a68368497f13/contracts/vaults/base/RibbonVault.sol#L64), [CapSet](https://github.com/ribbon-finance/ribbon-v2/blob/3fa3bec15ad1e2b18ad87f979b87a68368497f13/contracts/vaults/base/RibbonVault.sol#L72) and [Withdraw](https://github.com/ribbon-finance/ribbon-v2/blob/3fa3bec15ad1e2b18ad87f979b87a68368497f13/contracts/vaults/base/RibbonVault.sol#L74) events in `RibbonVault` should index their `address` arguments.
* Most of the [events](https://github.com/ribbon-finance/ribbon-v2/blob/3fa3bec15ad1e2b18ad87f979b87a68368497f13/contracts/vaults/RibbonThetaVault.sol#L32-L67) in `RibbonThetaVault` should index their `address` arguments.
* The [events](https://github.com/ribbon-finance/ribbon-v2/blob/3fa3bec15ad1e2b18ad87f979b87a68368497f13/contracts/libraries/GnosisAuction.sol#L18-L31) in `GnosisAuction` should index their `address` arguments.
* The [events](https://github.com/ribbon-finance/ribbon-v2/blob/3fa3bec15ad1e2b18ad87f979b87a68368497f13/contracts/utils/StrikeSelection.sol#L34-L35) in `StrikeSelection` should index their `address` arguments.

Events missing important parameters include:

* The [Deposit](https://github.com/ribbon-finance/ribbon-v2/blob/3fa3bec15ad1e2b18ad87f979b87a68368497f13/contracts/vaults/base/RibbonVault.sol#L62) event in `RibbonVault` does not emit the address of the account performing the deposit.
* The [CollectVaultFees](https://github.com/ribbon-finance/ribbon-v2/blob/3fa3bec15ad1e2b18ad87f979b87a68368497f13/contracts/vaults/base/RibbonVault.sol#L76-L80) event [does not emit the feeRecipient nor the managementFee](https://github.com/ribbon-finance/ribbon-v2/blob/3fa3bec15ad1e2b18ad87f979b87a68368497f13/contracts/vaults/base/RibbonVault.sol#L537).

Event inconsistencies include:

* The [Deposit](https://github.com/ribbon-finance/ribbon-v2/blob/3fa3bec15ad1e2b18ad87f979b87a68368497f13/contracts/vaults/base/RibbonVault.sol#L62), [InitiateWithdraw](https://github.com/ribbon-finance/ribbon-v2/blob/3fa3bec15ad1e2b18ad87f979b87a68368497f13/contracts/vaults/base/RibbonVault.sol#L64), [Redeem](https://github.com/ribbon-finance/ribbon-v2/blob/3fa3bec15ad1e2b18ad87f979b87a68368497f13/contracts/vaults/base/RibbonVault.sol#L66) and [CollectVaultFees](https://github.com/ribbon-finance/ribbon-v2/blob/3fa3bec15ad1e2b18ad87f979b87a68368497f13/contracts/vaults/base/RibbonVault.sol#L76) events use inconsistent parameter types for rounds in `RibbonVault`.

Sensitive actions that are lacking events include, but are not limited to:

* The [setFeeRecipient](https://github.com/ribbon-finance/ribbon-v2/blob/3fa3bec15ad1e2b18ad87f979b87a68368497f13/contracts/vaults/base/RibbonVault.sol#L159) function in `RibbonVault`
* The [setStrikePrice](https://github.com/ribbon-finance/ribbon-v2/blob/3fa3bec15ad1e2b18ad87f979b87a68368497f13/contracts/vaults/RibbonThetaVault.sol#L321) function in `RibbonThetaVault`
* The [baseInitialize](https://github.com/ribbon-finance/ribbon-v2/blob/3fa3bec15ad1e2b18ad87f979b87a68368497f13/contracts/vaults/base/RibbonVault.sol#L117) function in `RibbonVault` does not emit events for most of the state variables it sets.
* The [initialize](https://github.com/ribbon-finance/ribbon-v2/blob/3fa3bec15ad1e2b18ad87f979b87a68368497f13/contracts/vaults/RibbonThetaVault.sol#L105) function in `RibbonThetaVault` does not emit events for most of the state variables is sets.
* The [initialize](https://github.com/ribbon-finance/ribbon-v2/blob/3fa3bec15ad1e2b18ad87f979b87a68368497f13/contracts/vaults/RibbonDeltaVault.sol#L91) function in `RibbonDeltaVault` does not emit events for most of the state variables is sets.

Consider more completely indexing existing events, adding new indexed parameters where they are lacking, and being consistent with event argument types to avoid hindering the task of off-chain services searching and filtering for events. Consider emitting all events in such a complete manner that they could be used to rebuild the state of the contract.

**Update**: _Partially fixed in commit [1d3e518eed09598c1f9a9105c94032a96a12de6e of PR#82](https://github.com/ribbon-finance/ribbon-v2/pull/82/commits/1d3e518eed09598c1f9a9105c94032a96a12de6e)._
