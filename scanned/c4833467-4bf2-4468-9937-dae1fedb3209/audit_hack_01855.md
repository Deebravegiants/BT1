# [M] Reentrancy in `executeTransaction()`

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

In `MixinTransactions`, `executeTransaction()` and `batchExecuteTransactions()` do not have the `nonReentrant` modifier. Because of that, it is possible to execute nested transactions or call these functions during other reentrancy attacks on the exchange. The reason behind that decision is to be able to call functions with `nonReentrant` modifier as delegated transactions.

Nested transactions are partially prevented with a separate check that does not allow transaction execution if the exchange is currently in somebody else's context:


**code/contracts/exchange/contracts/src/MixinTransactions.sol:L155-L162**
```solidity
// Prevent `executeTransaction` from being called when context is already set
address currentContextAddress_ = currentContextAddress;
if (currentContextAddress_ != address(0)) {
    LibRichErrors.rrevert(LibExchangeRichErrors.TransactionInvalidContextError(
        transactionHash,
        currentContextAddress_
    ));
}
```

This check still leaves some possibility of reentrancy. Allowing that behavior is dangerous and may create possible attack vectors in the future.

#### Recommendation

Add a new modifier to `executeTransaction()` and `batchExecuteTransactions()` which is similar to `nonReentrant` but uses different storage slot.
