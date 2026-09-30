# [M] Inconsistent QR and Decoding in dc4bc

## Summary
Severity: Medium
Contest weight: 0.1154
Dataset id: 14389
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
During fuzzing of the QR encoding and decoding functionality, the team identified several results where the encoded message did not match the decoded one. Some discrepancies were identified in how the QR libraries handled null bytes but, even when hex encoding prior to passing to the QR, and using alternative libraries, the inconsistencies persisted. Refer to fuzzing targets and crashes provided to the development team along with this report. The security risk is less associated with a malicious exploit, and more distributing malformed signatures.

## Recommendation
As the exact bugs associated with the fuzzing results could not be identified, the testing team recommends the following:  
• Hex-encode the message prior to encoding in QR, to avoid text encoding inconsistencies and null characters while allowing reasonable compression.  
• Display a secure hash of each QR payload (dechunked) on the hot and airgapped nodes - after the hot node  
• Consider prompting to confirm that these hashes match before proceeding.  
• Investigate fuzzing results and consider alternative QR encoding/decoding libraries if possible.
