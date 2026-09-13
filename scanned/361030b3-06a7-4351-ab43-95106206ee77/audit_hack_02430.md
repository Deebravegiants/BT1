# [M] Proposals cannot be canceled

## Summary
Severity: Medium
Source: https://github.com/compound-finance/comet/blob/2eb33b5e8454dba148373b6cb64ede4f7436fad7/contracts/bridges/BaseBridgeReceiver.sol#L107
Type: audit-issue

## Details
A proposal can queue its transactions in the `Timelock` contract by [processing the message](https://github.com/compound-finance/comet/blob/2eb33b5e8454dba148373b6cb64ede4f7436fad7/contracts/bridges/BaseBridgeReceiver.sol#L107) through the `BaseBridgeReceiver` contract.

However, even though the `Timelock` contract allows the `admin` address (in this case, the `BaseBridgeReceiver` contract) to [cancel a certain transaction](https://github.com/compound-finance/comet/blob/2eb33b5e8454dba148373b6cb64ede4f7436fad7/contracts/vendor/Timelock.sol#L67), the `BaseBridgeReceiver` contract does not implement the functionality to call that method.

This means that if a transaction needs to be canceled, a new proposal would need to be passed to change the `admin` address to an EOA or a contract that has the ability to cancel transactions. After the proposal is passed, it would need to be executed, and then the problematic transaction can finally be manually canceled.

Moreover, as the [executeProposal function](https://github.com/compound-finance/comet/blob/2eb33b5e8454dba148373b6cb64ede4f7436fad7/contracts/bridges/BaseBridgeReceiver.sol#L155) from the `BaseBridgeReceiver` contract is not access-controlled, any user may notice that a faulty or malicious transaction is queued and ready to be executed and the protocol will not have the option to stop them from executing it.

Consider implementing the functionality to cancel a transaction in the `BaseBridgeReceiver` contract.

_**Update:** Acknowledged, not resolved. The Compound team stated:_

> _L2Timelock proposals cannot be canceled by design._
> 
> _Transactions begin as a proposal on L1\. The L1 proposal is placed in the L1 Timelock (where it can be canceled), is queued for a period of time, and then is executed._
> 
> _The execution of the L1 proposal results in the transaction being enqueued on the L2\. It is in a pending state for a period of time, but as far as governance is concerned it is as though the proposal has already been executed._
> 
> _We accept that once a transaction is enqueued on the L2, there is no way to cancel it._
> 
> _Canceling an L2 proposal would require granting the authority to cancel to some entity on the L2; this is undesirable since the ability to cancel proposals is also a power that could be used maliciously._
