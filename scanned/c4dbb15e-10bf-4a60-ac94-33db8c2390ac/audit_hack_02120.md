# [M] 6.4 The Index Is Not Masked

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Medium Version 1 Code Corrected

The IDX_VALUE_MASK is not applied to index values at certain places:

```
1.Mask is not applied on the index in VM smart contract at line 94.
```

```
2.Mask is not applied on the index in CommandBuilder smart contract at line 396.
```
Code corrected:

The appropriate index masking has been applied.
