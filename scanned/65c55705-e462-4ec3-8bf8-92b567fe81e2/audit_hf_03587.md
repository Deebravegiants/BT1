# [C] SNAP-1 | Cardinality Errantly Incremented

## Summary
Severity: Critical
Contest weight: 0.0918
Dataset id: 19566
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the write function, if the cardinality is less than the size then the cardinality is always incremented, regardless of if a new index was written to or not. This perturbs the checking of the oldest snapshot on line 68 in the find function as well as everything in the search function.

## Recommendation
Only increment the cardinality when a new index is written to in the write function.
