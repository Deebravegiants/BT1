# [H] `CodeDelegationTransactionDecoder.decodeInnerPayload` reads the per-authorisation `chainId` as an unbounded `BigInteger`, but `MainnetTransactionValidator.validateTransactionType` enforces `chainId < 2^256` by **throwing an unchecked `IllegalArgument

## Summary
Severity: High
Chain: Ethereum
Component: hyperledger/besu
CWE: Improper Handling of Exceptional Conditions
Published: 2026-08-10
Source: https://github.com/besu-eth/besu/security/advisories/GHSA-pmrq-5v5f-x6mf
Type: github-advisory

## Details
**Summary**: `CodeDelegationTransactionDecoder.decodeInnerPayload` reads the per-authorisation `chainId` as an unbounded `BigInteger`, but `MainnetTransactionValidator.validateTransactionType` enforces `chainId < 2^256` by **throwing an unchecked `IllegalArgumentException`** rather than returning a `ValidationResult`. That exception propagates through `TransactionPool.validateTransaction → addTransaction → addRemoteTransactions` (none of which catch `IllegalArgumentException`) and aborts the entire `Collectors.toMap(...)` collector that is processing a peer's transactions batch. The peer is **not disconnected** (only `RLPException` triggers disconnect); the worker thread silently drops every transaction that came after the poisonous one.

**Severity**: High

**Affected file/line**:
- `ethereum/core/src/main/java/org/hyperledger/besu/ethereum/core/encoding/CodeDelegationTransactionDecoder.java:86` (unbounded `readBigIntegerScalar` for chainId)
- `ethereum/core/src/main/java/org/hyperledger/besu/ethereum/mainnet/MainnetTransactionValidator.java:170-184` (`throw new IllegalArgumentException(...)` mid-validation)
- `ethereum/eth/src/main/java/org/hyperledger/besu/ethereum/eth/transactions/TransactionPool.java:215-238` (`addTransaction` does not catch the exception)
- `ethereum/eth/src/main/java/org/hyperledger/besu/ethereum/eth/transactions/TransactionPool.java:180-195` (`addRemoteTransactions` collector cancels on the throw)
- `ethereum/eth/src/main/java/org/hyperledger/besu/ethereum/eth/transactions/TransactionsMessageProcessor.java:78-115` (catch only `RLPException`, not `IllegalArgumentException`)

## Vulnerability

EIP-7702 inner authorisations are decoded one chain id at a time:

```java
// CodeDelegationTransactionDecoder.java:83-101
public static CodeDelegation decodeInnerPayload(final RLPInput input) {
  input.enterList();

  final BigInteger chainId = input.readBigIntegerScalar();      // <-- no upper bound on size
  final Address address    = Address.wrap(input.readBytes());
  final long nonce         = input.readLongScalar();

  final byte yParity       = (byte) input.readUnsignedByteScalar();
  final BigInteger r       = input.readUInt256Scalar().toUnsignedBigInteger();
  final BigInteger s       = input.readUInt256Scalar().toUnsignedBigInteger();

  input.leaveList();

  final SECPSignature signature =
      SIGNATURE_ALGORITHM.createCodeDelegationSignature(r, s, yParity);

  return new org.hyperledger.besu.ethereum.core.CodeDelegation(
      chainId, address, nonce, signature);
}
```


_Trimmed to 38 lines — full report: https://github.com/besu-eth/besu/security/advisories/GHSA-pmrq-5v5f-x6mf_
