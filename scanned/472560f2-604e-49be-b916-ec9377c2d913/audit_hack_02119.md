# [H] 6.1 Function writeOutputs Can Corrupt Memory

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness High Version 1 Code Corrected

To store the pointer of the return data the writeOutputs function performs a write to memory at the
index state + 32 + (idx & IDX_VALUE_MASK) * 32. However, a check that this location still
belongs to the state array of pointers is not performed. This effectively permits writing to locations in
memory that can contain other variables, including data of other state elements. The command
(maliciously or accidentally) can trigger such writing and cause unexpected results.

Code corrected:

A check was introduced that verifies that idx & IDX_VALUE_MASK < state.length.
