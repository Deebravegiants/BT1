# [H] Insufficient PSBT validation

## Summary
Severity: High
Contest weight: 0.2952
Dataset id: 15147
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The validate_psbt() function is executed when a signing package is received from a peer during a FROST signing round. It ensures the psbt is correctly formatted and contains the correct inputs and outputs before it is signed.
However, there are two places where the outputs of the psbt are not sufficiently validated:
• In validate_psbt_by_ids() it is checked that for each peg-out in the psbt there is a corresponding event on the chain. However, it only checks peg-outs that are in the psbt.outputs vector. The actual transaction outputs psbt.unsigned_tx.output are not checked. This allows a malicious coordinator to add an arbitrary output to psbt.unsigned_tx.output without the validation failing.
• validate_psbt() ensures that all pending peg-outs are included in the psbt. However, it does not check that all outputs of the psbt are pending peg-outs. As such a malicious coordinator may include outputs in psbt that are not pending peg-outs.
The issue is rated as high as it allows a malicious user to include invalid outputs which will be signed by the Federation multisig, causing Bitcoin to be released on L1. The issue is restricted to the coordinator as they are the only actor who may initiate a signing round to create a psbt and send it to the other signers. Therefore, the likelihood is rated as medium as the coordinator is required to perform the attack.

## Recommendation
Ensure the psbt is sufficiently validated such that it only contains valid peg-outs.
