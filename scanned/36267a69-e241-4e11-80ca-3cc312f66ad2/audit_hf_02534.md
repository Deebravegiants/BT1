# [H] retryRedeem() can be used to block the LayerZero pathway

## Summary
Severity: High
Contest weight: 0.1560
Dataset id: 13534
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There is no validation of bytes passed as options to _lzSend() inside the retryRedeem() function. An attacker can encode the adapterParams and specify a very small gasLimit for the relayer to deliver the message to the destination chain. A transaction with such a small gas limit would revert inside the lzReceive() function due to out-of-gas exception. As a consequence, it would end up as storedPayload inside the Endpoint contract. This would block the delivery of all the subsequent messages until the payload is cleared.

## Recommendation
There should be validation that a certain minimum gas is specified while leaving the user an option of airdropping tokens to the destination chain. See adapterParams for more details.
