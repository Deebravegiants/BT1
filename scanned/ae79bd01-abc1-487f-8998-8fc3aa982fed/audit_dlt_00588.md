# [?] forkchoice: fix forkchoice balance underflow when att slot change (#16520)

## Summary
Severity: Unknown
Chain: Ethereum
Component: prysmaticlabs/prysm
Published: 2026-03-13
Source: https://github.com/OffchainLabs/prysm/commit/6605dfbd502422c61154f2e21655ae8f8621b109
Type: security-commit

## Details
forkchoice: fix forkchoice balance underflow when att slot change (#16520)

In ePBS, `resolveVoteNode` routes validator balances to two different
accumulators based on the attestation slot:

When a validator re-attests for the **same block** in a **new epoch**
(assigned to a different slot), the root and payload status are
unchanged. The trigger condition:

  ```go
if vote.currentRoot != vote.nextRoot || oldBalance != newBalance ||
vote.currentPayloadStatus != vote.nextPayloadStatus {
```
  ...does not fire, so the balance is never moved. But the vote rotation silently updates currentSlot to the new value. On the next vote change, the subtraction targets the wrong accumulator (which has balance=0), causing the underflow.

  Examples:
  1. Epoch 2: Validator attests at slot 95 for block B (slot 95).
  pending = (95 == 95) = true → 32 ETH added to `Node.balance`
  2. Epoch 3: Validator re-attests at slot 96 for same block `B.Root/payloadStatus` went from pending to empty → not reprocessed. And currentSlot rotated to 96.
  3. Epoch 4: Validator attests for block C. Subtract from B that's no longer pending but has zero balance which triggers underflow
