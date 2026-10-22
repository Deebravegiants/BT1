# [M] Orders with `tokenAmt` of `type

## Summary
Severity: Medium
Contest weight: 0.3671
Dataset id: 15129
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability concerns the cancellation logic of a decentralized exchange order. When an order is cancelled, the contract records the amount that has been filled by assigning the stored value `filled[hashStruct] = o.tokenAmt + 1`. This extra increment is unnecessary and creates an arithmetic overflow when the order’s `tokenAmt` field contains the maximum possible unsigned integer (`type(uint256).max`). In Solidity versions that enforce checked arithmetic, the addition of 1 to the maximum value triggers a runtime revert, causing the `cancelOrder` transaction to fail. Consequently, any order that is deliberately crafted with a `tokenAmt` equal to the maximum uint256 becomes uncancellable, effectively locking the associated funds and preventing the user from withdrawing or modifying the order. The issue is discovered during a code audit that highlighted the unusual `+ 1` operation and confirmed the overflow by reproducing the failure in a proof‑of‑concept test. It is difficult to notice in normal operation because typical orders never use the maximum integer value, so the overflow only appears under a deliberately extreme input. The impact is a denial‑of‑service on a per‑order basis: the order creator or any participant who interacts with the order sees the transaction revert, receives no confirmation of cancellation, and may be unable to retrieve the locked assets. The bug belongs to the class of unchecked arithmetic overflow errors that break business logic assumptions about order lifecycle management. To remediate, the contract should assign the exact token amount without the extra increment, i.e., `filled[hashStruct] = o.tokenAmt`, ensuring that the stored filled amount matches the intended value and that cancellation works for all valid inputs. From the user’s perspective, the UI would display a cancellation attempt that never succeeds, often showing an error or a reverting transaction, while the expected behaviour—receiving a cancellation confirmation and regaining control of the funds—fails. This mismatch between expectation (order can be cancelled) and reality (transaction always reverts) violates the protocol’s accounting guarantees and can be exploited as a targeted denial‑of‑service attack against specific orders.

## Proof of Concept
```solidity
filled[hashStruct] = o.tokenAmt + 1;
```

`cancelOrder` will overflow in the line shown above if `o.tokenAmt` is `type(uint256).max` causing the transaction to always revert for that order.

## Recommendation
I don’t see any reason why 1 should be added to `o.tokenAmt`, change to:
    
    filled[hashStruct] = o.tokenAmt;
