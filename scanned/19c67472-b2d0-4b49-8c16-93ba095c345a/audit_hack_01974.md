# [M] 6.29 Missing Delay Restriction in BaseValidator

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Medium Version 1 Code Corrected

Setting the new params in BaseValidator follows the pattern stage-wait-commit. On staging the new
parameters, the respective timestamp is updated:

```
_stagedValidatorParamsTimestamp = block.timestamp + governance.governanceDelay;
```
However, the admin of the governance can commit the staged parameters at any time, e.g.,
immediately after staging them, by calling commitValidatorParams as the function does not check if
the delay period has passed.

Code corrected:

The function now checks the delay with a require validating
block.timestamp >= _stagedValidatorParamsTimestamp.
