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
```

_Trimmed to 38 lines — full report: https://github.com/advisories/GHSA-hfcf-v2f8-x9pc_
