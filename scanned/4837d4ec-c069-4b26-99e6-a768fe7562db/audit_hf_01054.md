# [M] Changes in modules not detected

## Summary
Severity: Medium
Contest weight: 0.1122
Dataset id: 4030
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The function validatePostExecutorTransaction() checks the executor plugin is still enabled. However other modules are not checked. As modules are very powerful, if they would be "sneaked" in, they would pose risks to the safes.
function validatePostExecutorTransaction(address, /*msgSender */ address account) external view {
// ...
// Check if account has executor plugin still enabled as a module on it
if (!IGnosisSafe(account).isModuleEnabled(AddressProviderService._getAuthorizedAddress(_EXECUTOR_PLUGIN_HASH))) {
revert InvalidExecutorPlugin();
}
// ...
}

## Recommendation
Consider checking the list of modules. This could be done by letting the trusted verifier sign the list of modules that should be present after the transaction and verifying that in the Post functions. For validatePostExecutorTransaction() this is relatively straightforward. For the validatePostTransaction functions, see the issue "Changes between signing and execution could yield results that are outside the bounds of the policy" for a potential approach to perform checks.
