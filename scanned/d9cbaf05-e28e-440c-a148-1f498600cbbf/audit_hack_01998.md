# [M] 7.2 If Condition Always True

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Corrected

During the execution of function execute the following check is performed:

```
if (statusCode != "mgv/notExecuted") {
dirtyDeleteOffer(
...
);
}
```
However statusCode cannot have the value mgv/notExecuted at this point so the condition is always
true.

Code Corrected:

The code now runs unconditionally.
