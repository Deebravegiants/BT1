# [H] executeTransactionFromOutside does not increment the nonce

## Summary
Severity: High
Contest weight: 0.2671
Dataset id: 6490
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
ClaveImplementation implements executeTransactionFromOutside, which can be called by the wallet owner to manually execute a transaction as a fallback. However, this execution doesn't increment the nonce of the wallet.
function executeTransactionFromOutside(
Transaction calldata transaction
) external payable override {
// Check if msg.sender is authorized
if (!_k1IsOwner(msg.sender)) {
revert Errors.UNAUTHORIZED_OUTSIDE_TRANSACTION();
// Extract hook data from transaction.signature
bytes[] memory hookData = SignatureDecoder.decodeSignatureOnlyHookData(
transaction.signature
// Get the hash of the transaction
bytes32 signedHash = transaction.encodeHash();
// Run the validation hooks
if (!runValidationHooks(signedHash, transaction, hookData)) {
revert Errors.VALIDATION_HOOK_FAILED();
_executeTransaction(transaction);
Consider a scenario where the execution operator is unresponsive, and the wallet owner decides to manually execute the transaction. When the operator becomes active again and processes the request, it can still execute the transaction because the nonce is not incremented when executeTransactionFromOutside is called, potentially causing unintended double execution.

## Recommendation
Increment nonce inside executeTransactionFromOutside execution.
