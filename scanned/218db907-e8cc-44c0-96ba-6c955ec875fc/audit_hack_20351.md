# [M] 5.1.3 Changes in modules not detected

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk

**Context:** TransactionValidator.sol#L134-L

**Description:** The functionvalidatePostExecutorTransaction()checks the executor plugin is still enabled.
However other modules are not checked. As modules are very powerful, it they would be "sneaked" in, they
would pose risks to the safes.

```
function validatePostExecutorTransaction(address,/*msgSender */ address account) external view {
// ...
// Check if account has executor plugin still enabled as a module on it
if (!IGnosisSafe(account).isModuleEnabled(AddressProviderService._getAuthorizedAddress(_EXECUTOR_PLc
UGIN_HASH)))
{
```
```
,!
,!
revert InvalidExecutorPlugin();
}
// ...
}
```
**Recommendation:** Consider checking the list of modules. This could be done by letting the trusted verifier sign
the list of modules that should be present after the transaction and verifying that in the Post functions. Forvali-
datePostExecutorTransaction()this is relatively straightforward. For thevalidatePostTransactionfunctions,
see the issue "Changes between signing and execution could yield results that are outside the bounds of the
policy" for a potential approach to perform checks.

**Brahma:** Acknowledged.

**Spearbit:** Acknowledged.
