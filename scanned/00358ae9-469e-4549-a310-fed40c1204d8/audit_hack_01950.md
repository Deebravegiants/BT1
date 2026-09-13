# [M] 6.7 OperationRegistry: No Entry, No Checks

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Corrected


When there is no operation stored for a name, getOperation() returns an empty array and
subsequently nothing is checked. Shouldn’t this case be handled explicitly to avoid not checking
correctness by accident?

An operation name is a string. This allows displaying the operation name in a human readable way.
However, this can be dangerous as strings support the Unicode charset and many lookalike characters of
different alphabets exist in this charset. Hence users might be tricked.

For more insights into lookalike characters, please refer to:
https://util.unicode.org/UnicodeJsps/confusables.jsp?a=IncreaseMultipleWithFl

Code corrected:

getOperation() of OperationRegistry now reverts on non-existing operations instead of returning an
empty array (which results in skipping checks). Custom operation with empty actions have to be explicitly
added to the OperationRegistry.
