# [M] _enablePolicies() does not install ERC7739Content

## Summary
Severity: Medium
Contest weight: 0.1032
Dataset id: 5854
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the validateUserOp() function, the _enablePolicies() logic allows an account to atomically install policies during validation. Part of the data that's provided to the installation logic is enableData.sessionToEnable.erc7739Policies.allowedERC7739Content, which is an array of type names that are allowed to be used during an ERC-7739 compliant isValidSignature() call.
Despite this data being provided to _enablePolicies(), there is currently no logic to use it. As a result, accounts that install policies through _enablePolicies() will have incorrectly installed permissions, and future calls to isValidSignature() will fail.

## Recommendation
Add logic to _enablePolicies() to install enableData.sessionToEnable.erc7739Policies.allowed
// Enable ERC1271 policies
$erc1271Policies.enable({
