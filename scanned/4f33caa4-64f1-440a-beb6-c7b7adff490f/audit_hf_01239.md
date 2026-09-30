# [H] Checking for message expiration after receipt processing prevents pruning indexes, increase resources

## Summary
Severity: High
Contest weight: 0.1570
Dataset id: 5739
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the present implementation the initiating message/s timestamp is checked for expiration after the message is retrieved from the block. This defeats the purpose of limiting the need of keeping receipts indexed forever -- and actually make nodes that prune their indexes unable to prove a state transition.  
Running the op-program would require having all receipts from all blocks available regardless of expiration settings, since any message from any receipt from any block might need to be retrieved for validation.

## Recommendation
The check for expiration should be moved to just after the block header is retrieved in CanonBlockByNumber (or in Contains) and before any further data from the block is retrieved (especially the receipts).
