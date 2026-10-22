# [M] 3.2.2.1 Pending transaction positions not properly tracked when messages are skipped

## Summary
Severity: Medium
Contest weight: 0.4766
Dataset id: 5156
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The current integration with the Espresso network lacks proper transaction validation in the EspressoFinalityNode, allowing potential malicious transactions to be processed until they are eventually rejected by the L1 sequencing contract. While this does not compromise the final ordering or validity of transactions (due to TEE verification on L1), it creates unnecessary overhead for nodes processing these unvalidated transactions.
The EspressoFinalityNode.createBlock() function processes transactions from the Espresso network without validating their authenticity or origin. The only validation performed is checking if transactions can be properly deserialized:
```solidity
for _, tx := range arbTxns.Transactions {
    var out types.Transaction
    // signature from the data poster is the first 65 bytes of a transaction
    tx = tx[65:]
    if err := out.UnmarshalBinary(tx); err != nil {
        log.Warn("malformed tx found")
        continue
    }
    txes = append(txes, &out)
}
```
This means that any actor can submit transactions to the Espresso network, which will be processed by nodes until they are ultimately rejected at the L1 sequencing contract level where TEE proofs are properly verified.
Impact: The impact is medium. While the final sequencing security is maintained through L1 TEE verification, the lack of transaction validation means:
1. Node operators cannot distinguish between valid and invalid transactions before L1 confirmation.
2. Nodes waste resources processing potentially invalid transactions.
3. Network bandwidth is consumed by transactions that will eventually be rejected.
Likelihood: The likelihood is medium. The current design makes it straightforward for anyone to submit transactions to the network. However, an actual attack requires preparation and various conditions.

## Proof of Concept
// pendingTxnsPos = [0, 1, 2, 3]
// msg at position 1 is nil
// msgs will contain messages from positions [0, 2, 3]
// msgCnt = 3
// Code will incorrectly mark positions [0, 1, 2] as submitted
// Position 1 was never actually processed but is marked as submitted

## Recommendation
Consider implementing transaction validation that includes TEE verification proofs at the Espresso network level. This would allow nodes to reject invalid transactions early, reducing unnecessary resource consumption.
The current integration should be reevaluated to determine if the added complexity provides sufficient benefits given that the critical security properties are ultimately enforced through L1 TEE verification.
