# [M] M-20 | Signature Replay In MuxPriceProvider Contract

## Summary
Severity: Medium
Contest weight: 0.1424
Dataset id: 2121
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The getOraclePrice function in the MuxPriceProvider requires oracleData.sequence to be greater than the sequence of the contract. It doesn’t specifically require it to be the next sequence, nor does it require it to be greater than the sequence of the last accepted oracle data. When a valid signature sequence is beyond the contract’s sequence, this signature can be used repeatedly by the broker until the sequences match. For example, if the current contract sequence is 4 and oracle data with a sequence of 10 is used, the contract sequence will be updated to 5. Another oracle data with a sequence of 8 would still be considered valid. Assuming this is expected behavior, any broker can repeatedly call the getOraclePrice function, increment the contract's sequence to 10, and render the oracle data with a sequence of 8 invalid.

## Recommendation
If oracle data is expected to be ordered and the behavior described above is not acceptable, either enforce the oracle sequence to be the exact next sequence or update the contract sequence to the latest accepted oracle data. This ensures that oracle data with a smaller sequence will not be valid. If unordered oracle data is the intended behavior, consider implementing access control for the getOraclePrice function.
