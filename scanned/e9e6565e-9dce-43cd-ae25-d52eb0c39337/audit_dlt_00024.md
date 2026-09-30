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

`readBigIntegerScalar` (`BytesValueRLPInput.java:365`) calls `checkScalar("arbitrary precision scalar")` with no length argument, so any RLP-permitted length is accepted. A peer can encode a 33-byte (or larger) chainId, e.g. `chainId = 2^256`, and the decoder will happily build a `CodeDelegation` with that value.

Validation later trips on this with an *uncaught* exception:

```java
// MainnetTransactionValidator.java:164-188
final Optional<ValidationResult<TransactionInvalidReason>> validationResult =
    transaction
        .getCodeDelegationList()
        .map(
            codeDelegations -> {
              for (CodeDelegation codeDelegation : codeDelegations) {
                if (codeDelegation.chainId().compareTo(TWO_POW_256) >= 0) {
                  throw new IllegalArgumentException(                              // <-- runtime throw
                      "Invalid 'chainId' value, should be < 2^256 but got "
                          + codeDelegation.chainId());
                }
                if (codeDelegation.r().compareTo(TWO_POW_256) >= 0) { ... throw ... }
                if (codeDelegation.s().compareTo(TWO_POW_256) >= 0) { ... throw ... }
              }
              return ValidationResult.valid();
            });
```

(The `r`/`s` branches above are dead code because `readUInt256Scalar` clamps to 32 bytes already, but the `chainId` branch is reachable.)

The validator's caller does not catch this:

```java
// TransactionPool.java:396-427
private ValidationResultAndAccount validateTransaction(
    final Transaction transaction, final boolean isLocal, final boolean hasPriority) {
  ...
  final ValidationResult<TransactionInvalidReason> basicValidationResult =
      getTransactionValidator()
          .validate(
              transaction,
              chainHeadBlockHeader.getBaseFee(),
              Optional.of(Wei.ZERO),
              TransactionValidationParams.transactionPool());           // <-- can throw IllegalArgumentException
  if (!basicValidationResult.isValid()) {
    return new ValidationResultAndAccount(basicValidationResult);
  }
  ...
}
```

Neither does its caller:

```java
// TransactionPool.java:215-238
private ValidationResult<TransactionInvalidReason> addTransaction(
    final Transaction baseTransaction,
    final boolean isLocal,
    final boolean hasPriority,
    final byte score) {
  ...
  final ValidationResultAndAccount validationResult =
      validateTransaction(transaction, isLocal, hasPriority);          // <-- exception escapes
  ...
}
```

And the *batch* caller propagates the throw out of the stream collector, killing the entire collection:

```java
// TransactionPool.java:180-195
final var validationResults =
    sortedBySenderAndNonce(transactions)
        .collect(
            Collectors.toMap(
                Transaction::getHash,
                transaction -> {
                  final boolean hasPriority = isPriorityTransaction(transaction, false);
                  final var result = addTransaction(transaction, false, hasPriority, MAX_SCORE);    // <-- throws
                  if (result.isValid()) { addedTransactions.add(transaction); }
                  ...
                  return result;
                },
                ...));
```

`Collectors.toMap` aborts on the first thrown lambda, so every transaction queued behind the poisonous one in `sortedBySenderAndNonce` is silently dropped. Honest peers' transactions in the same batch are lost.

The wire-side handler that called `addRemoteTransactions` only catches `RLPException`:

```java
// TransactionsMessageProcessor.java:80-116
try {
  ...
  transactionPool.addRemoteTransactions(freshTransactions);    // <-- IllegalArgumentException leaks through
} catch (final RLPException ex) {
  if (peer != null) {
    LOG.debug("Malformed transaction message ... disconnecting: {}", peer, ex);
    peer.disconnect(DisconnectReason.BREACH_OF_PROTOCOL_MALFORMED_MESSAGE_RECEIVED);
  }
}
```

So:

1. The malicious peer is **not disconnected**.
2. The exception bubbles up to `EthScheduler.txWorkerExecutor.execute(command)` and is logged by the executor's default `UncaughtExceptionHandler`. The `EthPeer` connection stays alive.
3. Every transaction in the batch after the poisonous one is silently dropped — including legitimate transactions the peer relayed from other honest peers.

## Impact

- **Peer-triggered transaction-batch drop, undetected**: an attacker controlling one peer can drop every other peer's transactions by intermixing one bad EIP-7702 transaction per batch. From the operator's view, the node "just doesn't see" specific transactions. This is a **censorship primitive** that bypasses the usual mempool replacement / spam guards because the bad tx never reaches the pool.
- **Malicious peer never disconnects**, so the same peer can keep sending poisoned batches forever. Other reputation signals (slow-response, equivocation) are not triggered because the rest of the peer's behaviour can be perfectly normal.
- **Stack-trace log spam** by `EthScheduler.txWorkerExecutor`'s uncaught handler: each malicious tx logs a multi-line stack trace, easily 30+ lines. With persistent flooding, log volume grows and hides legitimate operational signal.
- **API-side exposure**: the same `IllegalArgumentException` can also be triggered by `eth_sendRawTransaction` (the JSON-RPC handler does catch generic `RuntimeException` and returns 500, so this surface is "only" a 500 error per call, not a worker drop — but it still leaks an internal stack trace if `--Xrpc-stack-trace=true`).
- **The vulnerable validator path is reached for any post-Prague EIP-7702 transaction**, which is now mainnet-active.

## PoC

A minimal RLP for an EIP-7702 transaction with one authorisation whose chainId is exactly `2^256` (33 bytes, all zero except the leading 0x01):

```
0x04                                              # transaction type = SET_CODE
[ chainId = 1 ,
  nonce   = 0 ,
  maxPriorityFeePerGas = 0 ,
  maxFeePerGas        = 1_000_000_000 ,
  gasLimit            = 100_000 ,
  to                  = 0x...20 bytes... ,
  value               = 0 ,
  data                = 0x ,
  accessList          = [] ,
  authorizationList   = [
    [ chainId = 0x01<32 zero bytes>           # 0x10000000000000000000000000000000000000000000000000000000000000000 (= 2^256)
    , address = 0x...20 bytes...
    , nonce   = 0
    , yParity = 0
    , r       = 0x...32 bytes...
    , s       = 0x...32 bytes...
    ]
  ] ,
  yParity, r, s
]
```

Signed with any valid sender key, sent over P2P:

```bash
$ besu-attacker --send-eth7702-batch \
    --tx '<good_tx_1>' \
    --tx '<malicious_tx_with_oversized_chainid>' \
    --tx '<good_tx_2>'
```

Result on the victim node:

```
[2024-XX-XX] WARN  EthScheduler - Uncaught exception in tx worker
java.lang.IllegalArgumentException: Invalid 'chainId' value, should be < 2^256 but got 115792089237316195423570985008687907853269984665640564039457584007913129639936
    at MainnetTransactionValidator.validateTransactionType(MainnetTransactionValidator.java:171)
    at MainnetTransactionValidator.validate(MainnetTransactionValidator.java:93)
    at TransactionPool.validateTransaction(TransactionPool.java:418)
    at TransactionPool.addTransaction(TransactionPool.java:238)
    at TransactionPool.lambda$addRemoteTransactions$N(TransactionPool.java:187)
    ...
```

`good_tx_2` is silently dropped; the peer that sent the malicious tx is still connected.

## Recommendation

1. **Replace the `throw` with a `ValidationResult.invalid(...)`** in `MainnetTransactionValidator`. This is consistent with the rest of the file (every other validation failure returns a `ValidationResult`):

   ```java
   for (CodeDelegation codeDelegation : codeDelegations) {
     if (codeDelegation.chainId().compareTo(TWO_POW_256) >= 0) {
       return Optional.of(ValidationResult.invalid(
           TransactionInvalidReason.INVALID_TRANSACTION_FORMAT,
           "code delegation chainId must be < 2^256"));
     }
     // r / s checks are dead code (see UInt256Scalar) — drop them.
   }
   ```

2. **Reject oversized chainId at decode time**. `CodeDelegationTransactionDecoder.decodeInnerPayload` should call `readUInt256Scalar()` (32-byte cap) instead of `readBigIntegerScalar()`, mirroring the way `r`/`s` are read. The chainId is bounded to `2^256-1` by the EIP, so anything larger is malformed RLP and should throw `RLPException` — which **is** caught by `TransactionsMessageProcessor` and triggers the peer disconnect.

3. **Add a defensive `catch (RuntimeException ex)` around the validator call** in `TransactionPool.addTransaction`. Even after fixes (1) and (2), it should not be possible for an unchecked exception in transaction validation to silently drop other peers' transactions. Treat it as `INVALID_TRANSACTION_FORMAT` and log at WARN.

4. **Broaden `TransactionsMessageProcessor`'s catch from `RLPException` to `Exception` (or at least `RLPException | IllegalArgumentException`)**. The peer is misbehaving in either case; the node should disconnect rather than silently drop.

5. The same code path exists in `BlobTransactionDecoder` and the other typed-tx decoders for fields read via `readBigIntegerScalar` — audit them while you are here. (Notably `BlobTransactionDecoder.readTransactionPayloadInner` reads the outer `chainId` via `readBigIntegerScalar` too; a similar oversize attack against an EIP-4844 transaction would fail later on signature verification rather than chainId range, but the unchecked exception pattern is the same.)

**Payment / Contact**
If this finding qualifies for a reward, payment can be sent to:
`0x83e033dd8ddb93052cc880227b06a8ee38f25eb2`
(EVM address — any chain)

Filing through GitHub PVR because the platform that hosts the official bounty has KYC requirements I have not been able to clear from my jurisdiction.
