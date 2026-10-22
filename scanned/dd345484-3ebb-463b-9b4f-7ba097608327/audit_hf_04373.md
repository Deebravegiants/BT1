# [H] H-01 | Layerzero Pathway will be Continuously Blocked

## Summary
Severity: High
Contest weight: 0.1754
Dataset id: 21580
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Currently, the OFT contract allows anyone to set the address(0) as a token recipient on the destination chain. However, this is a transaction that will always revert because the OpenZeppelin's implementation does not allow minting to the 0 address. An attacker can leverage this to block the LayerZero pathway. An example:
- The nonce on both chains is 5.
- An attacker successfully sends their minting tx and the nonce becomes 6.
- The transaction is received on the destination chain, but fails.
- Since the app uses ordered delivery, all subsequent transactions will be blocked until 6 is resolved. As a result, an attacker can keep blocking the LayerZero pathway.

## Recommendation
Don't allow sending cross-chain packages that mint to the address(0).
