# [H] bitcoinj has a ScriptExecution P2PKH/P2WPKH Verification Bypass

## Summary
Severity: High
Chain: org.bitcoinj:bitcoinj-core
Component: org.bitcoinj:bitcoinj-core
CVE: CVE-2026-44714
CWE: Improper Verification of Cryptographic Signature
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-hfcf-v2f8-x9pc
Type: github-advisory

## Details
### Summary
`ScriptExecution.correctlySpends()` contains two fast-path verification bugs for standard `P2PKH` and native `P2WPKH` spends in `core/src/main/java/org/bitcoinj/script/ScriptExecution.java`.

In both branches, bitcoinj verifies an attacker-controlled signature/public-key pair but fails to verify that the public key is the one committed to by the output being spent. As a result, any attacker keypair can satisfy bitcoinj's local verification for arbitrary `P2PKH` and `P2WPKH` outputs.

This doesn't affect the SPV (simple payment verification) trust model, as this model follows PoW and doesn't verify input signatures at all.

### Details
The issue is in the optimized branches of `ScriptExecution.correctlySpends(...)`.

In the `P2PKH` fast path at `core/src/main/java/org/bitcoinj/script/ScriptExecution.java:1042`, the code:

- parses the attacker-supplied signature from `scriptSig`
- parses the attacker-supplied public key from `scriptSig`
- computes the sighash against the victim output's `scriptPubKey`
- checks only `pubkey.verify(sigHash, signature)`

It never enforces the missing `P2PKH` binding:

- `HASH160(pubkey) == ScriptPattern.extractHashFromP2PKH(scriptPubKey)`

That means the `OP_DUP OP_HASH160 <hash> OP_EQUALVERIFY OP_CHECKSIG` semantics are not actually enforced in this fast path.

Relevant code:

```java
} else if (ScriptPattern.isP2PKH(scriptPubKey)) {
    if (chunks.size() != 2)
        throw new ScriptException(...);
    TransactionSignature signature;
    try {
        byte[] data = Objects.requireNonNull(chunks.get(0).data);
        signature = TransactionSignature.decodeFromBitcoin(data, true, true);
    } catch (SignatureDecodeException x) {
        throw new ScriptException(...);
    }
    ECKey pubkey = ECKey.fromPublicOnly(Objects.requireNonNull(chunks.get(1).data));
    Sha256Hash sigHash = txContainingThis.hashForSignature(scriptSigIndex, scriptPubKey,
            signature.sigHashMode(), false);
    boolean validSig = pubkey.verify(sigHash, signature);
    if (!validSig)
        throw new ScriptException(...);
}
```

In the native `P2WPKH` fast path at `core/src/main/java/org/bitcoinj/script/ScriptExecution.java:1023`, the bug is similar. The code:

- reads the attacker-supplied pubkey from `witness`
- builds `scriptCode` from that attacker pubkey with `ScriptBuilder.createP2PKHOutputScript(pubkey)`
- computes the BIP143 sighash using that attacker-derived `scriptCode`
- verifies the signature against the attacker pubkey

It never enforces:

- `HASH160(pubkey) == ScriptPattern.extractHashFromP2WH(scriptPubKey)`

So for `P2WPKH`, the attacker controls both the pubkey and the `scriptCode` used for signing.

Relevant code:

```java
if (ScriptPattern.isP2WPKH(scriptPubKey)) {
    Objects.requireNonNull(witness);
    if (witness.getPushCount() < 2)
        throw new ScriptException(...);
    TransactionSignature signature;
    try {
        signature = TransactionSignature.decodeFromBitcoin(witness.getPush(0), true, true);
    } catch (SignatureDecodeException x) {
        throw new ScriptException(...);
    }
    ECKey pubkey = ECKey.fromPublicOnly(witness.getPush(1));
    Script scriptCode = ScriptBuilder.createP2PKHOutputScript(pubkey);
    Sha256Hash sigHash = txContainingThis.hashForWitnessSignature(scriptSigIndex, scriptCode, value,
            signature.sigHashMode(), false);
    boolean validSig = pubkey.verify(sigHash, signature);
    if (!validSig)
        throw new ScriptException(...);
}
```

Affected call sites include:

- `core/src/main/java/org/bitcoinj/core/TransactionInput.java:546`
- `core/src/main/java/org/bitcoinj/wallet/Wallet.java:4520`
- `core/src/main/java/org/bitcoinj/signers/LocalTransactionSigner.java:84`
- `core/src/main/java/org/bitcoinj/signers/CustomTransactionSigner.java:77`

These call sites use `correctlySpends()` for transaction/input validation and pre-signing checks. Any application that treats a successful result from this path as proof that a spend is valid is affected.

### Fix
The issue is fixed on the `release-0.17` branch via 2bc5653c41d260d840692bc554690d4d79208f9c, and on `master` via b575a682acf614b9ff95cacbdeb48f86c3ababe0. A 0.17.1 maintenance release has been made available on Maven Central.
