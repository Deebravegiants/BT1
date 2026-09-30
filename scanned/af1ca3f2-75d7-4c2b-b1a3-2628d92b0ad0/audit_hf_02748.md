# [C] Peg-In Amounts May Be Stolen By Manipulating tx.gasprice

## Summary
Severity: Critical
Contest weight: 0.6119
Dataset id: 15103
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
While minting synthetic BTC in the L2 system, the refund value calculation uses tx.gasprice. The refund value is taken from the user's peg-in amount and given to the refundAddress. An attacker may manipulate this to reduce the funds distributed to the destination. ```solidity
uint256 txCost =
    (gasStart - gasleft()
    + GAS_INTERNAL_TRANSFER
    + GAS_INTERNAL_TRANSFER
    + GAS_AMOUNT_UPDATE
    + GAS_REVERT_TRUE
    + BASE_GAS_MINT_EVENT
    + metadata.length / 4 - 1)
    * tx.gasprice; // @audit tx.gasprice can be manipulated by sender
// 3 gas for comparison if true
require(txCost <= amount, "Tx cost exceeds pegin amount");
// snipped ...
(bool successRefund, ) = payable(refundAddress).call{value: txCost}("");
require(successRefund, "Refund to refundAddress failed");
```
After EIP-1559, the eﬀective gas price is calculated as base fee + priority fee (tip). In this case, a malicious block builder can use an unrealistically high tip to increase the gas price and inﬂate the refund amount. If the block builder is the one who submits the mint transaction, they would get the entire peg-in amount as a refund. Additionally, they would receive the priority fee back as block rewards. This way, the attacker could steal the user's entire peg-in amount. Furthermore, if the attacker is not a builder but a regular user who submits the mint transaction, they may execute the same attack. In this case, the attacker would get the entire transaction fee refunded while the user loses all their peg-in amount, eﬀectively creating a DoS attack on the peg-in process.

## Recommendation
A resolution is to use block.basefee instead of tx.gasprice while calculating the refund amount.
