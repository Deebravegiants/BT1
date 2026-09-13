# [M] 7.6 Undocumented Public Functions

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Corrected

Function wipeAndFreeGem of the MultiplyProxyActions contract is public. The function is only
used internally and there is no valid use case to call it directly. Direct calls to this function will likely fail
due to preconditions not being met. Furthermore the documentation does not list it as one of the public
functions.

Similarly _collectFee() of the Exchange contract is public despite being used only internally. Here
as well the documentation does not list _collectFee() as public function.


Code corrected:

The functions are now internal.
