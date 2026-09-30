# [M] Parameters and Payload Length Uncommitted Leading to Ambiguous Recover Behavior

## Summary
Severity: Medium
Contest weight: 0.1541
Dataset id: 5197
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Certain metadata like param including the recovery_threshold and total_weights and, more importantly, payload_byte_len are not part of the commitment. Instead these values are passed along in an unauthenticated manner as part of the shares. For example, metadata like payload_byte_len and num_polys are read from the zeroth share.
Consider the following concern: if payload_byte_len is not committed does that mean that the data can be arbitrarily truncated during decoding which might have implications for downstream execution? Currently, this function allows for arbitrary truncation.
Even without arbitrary truncation, there is a concern around ambiguous truncation of padded payloads. When the payload is not a multiple of field_bytes_len, the encoding pads with zeros during dispersal (See avid_m.rs#L182). Currently, the unauthenticated payload_byte_len is the only way to tell how to recover the correct data, i.e., truncate the correct number of padded zeros.

## Recommendation
The following can be implemented to prevent ambiguous recovery:
• Adding params and payload_byte_len to the commitment.
• Verifying that the shares include vectors with the appropriate number of evaluations (num_polys evaluations in each share vector where num_polys is computed from payload_byte_len and recovery_threshold) in verify_share.
