# [H] H-04 | Cant set data stream through config

## Summary
Severity: High
Contest weight: 0.1090
Dataset id: 21427
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When the setDataStream function is called there is a check that ensures the dataStream is not already set. However the check incorrectly does not reference the dataStore instead the check only uses the Keys.dataStreamIdKey(token) key. Which will never return 0. Which means the check will always fail and Data Streams will not be able to be added via the config.

## Recommendation
Reference Data Store when checking if the stream has already been added.
