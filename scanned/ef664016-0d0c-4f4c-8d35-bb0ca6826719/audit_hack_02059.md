# [M] 6.14 Redundant and Improper Revert Condition

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Corrected

The two functions balanceRisky() and balanceStable() verify if the call returns the balance
correctly by checking: if(!success && data.length < 32) and revert if the condition is true. This
makes sense if success is false or the call did not return a value (data.length < 32). With using
&& instead of or the condition would not revert for the combination of success = false and
data.length > 32 (which is possible). As the function needs the balance to work properly, we do not
see a case where this should not revert if data.length < 32. The data.length check is also


redundant because it is also performed in abi.decode(data, (uint256)). Additionally, it might
make sense to reevaluate if the less than condition makes sense or an equal condition would be more
suitable.

Code corrected

The client has updated the check as follows: if (!success || data.length < 32).
