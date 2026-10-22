# [M] Griefer beneficiary can cause DOS

## Summary
Severity: Medium
Contest weight: 0.4096
Dataset id: 15621
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a denial‑of‑service (DoS) condition that arises during the batch payout process of a Juicebox project when the contract pushes funds directly to each beneficiary. The root cause is the use of a push‑payment model – the contract calls a low‑level transfer (or ERC777 safe transfer) to the beneficiary address inside a loop that distributes the net payout amount to all configured splits. If any beneficiary is a contract that deliberately reverts in its fallback or token‑receive hook, the transfer call will throw, causing the entire _distributeToPayoutSplitsOf() transaction to revert. Because the Solidity revert propagates up the call stack, the remaining beneficiaries never receive their share, and the payout transaction is aborted. This can be exploited by a malicious or compromised beneficiary who simply implements a fallback function that reverts, or by using a token standard such as ERC777 that invokes a user‑defined hook which the attacker can make fail. When the attacker’s contract receives the forwarded amount, it triggers the revert, stopping the whole distribution.

The impact is that funds become temporarily unavailable: users and other beneficiaries see no balances increase, the UI may report a successful payout but on‑chain the transaction fails, and the project owner cannot complete the intended payout. In the worst case the funds remain locked in the contract until the malicious beneficiary is removed or the payout logic is changed, effectively creating a denial‑of‑service against the financial flows of the protocol. The condition occurs whenever a payout is executed with multiple beneficiaries and at least one of them is a contract capable of rejecting the incoming transfer. All participants – beneficiaries, project owners, and end users expecting refunds or revenue shares – are affected because the business logic assumes that each split will be paid atomically.

The issue was discovered during a Code4rena audit that inspected the payout routine and tested the behavior with native ETH and ERC777 tokens. The problem is subtle because the failure manifests only when a beneficiary deliberately reverts; normal users who receive funds with a benign address experience no error, so the bug can remain hidden until a malicious actor exploits it. It is a classic example of a "push‑payment" vulnerability where the contract’s logic does not handle a failed transfer gracefully.

To remediate, the contract should adopt a pull‑payment pattern: rather than sending funds directly, it should record each beneficiary’s entitlement and allow them to withdraw the amount themselves. Alternatively, the distribution loop could catch failed transfers and continue processing the remaining beneficiaries, or use a safeTransfer mechanism that does not revert on failure and logs the issue for later manual resolution. The conceptual fix is to eliminate the reliance on a single transaction succeeding for all beneficiaries, thereby preventing a single malicious beneficiary from aborting the entire payout and ensuring that the protocol’s accounting guarantees remain intact.

## Proof of Concept
```solidity
// If there's a beneficiary, send the funds directly to the beneficiary. Otherwise, send to the msg.sender.
_transferFrom(
  address(this),
  _split.beneficiary != address(0) ? _split.beneficiary : payable(msg.sender),
  _netPayoutAmount
);
```

If token used is native ETH or ERC777 a beneficiary can revert the transaction on the callback and DOS `_distributeToPayoutSplitsOf()` for all the other beneficiaries.

## Recommendation
Have beneficiaries withdraw their benefit instead of sending it to them.

By design. Project owners bring their own risks and opportunities when setting payout splits. Made clear [here](https://info.juicebox.money/dev/learn/risks#setting-a-distribution-limit-and-payout-splits).

A malicious or compromised beneficiary is not exactly under a project owner’s control. Implementing the recommended mitigation step would prevent the possibility of DOS while maintaining all privileges of project owner. No risks outlined in link below would be mitigated by the recommended mitigation, thus project owner would still have access to same range of functionalities. <https://info.juicebox.money/dev/learn/risks/#setting-a-distribution-limit-and-payout-splits>
