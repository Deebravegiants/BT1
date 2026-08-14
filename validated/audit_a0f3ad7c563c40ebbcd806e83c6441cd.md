### Title
Unsafe JS `number` summation of untrusted PSBT input/output amounts can silently overflow/lose precision in Ledger dummy-input fee-safety check - ([File: features/hw-ledger/src/module/assets/utils/psbt.ts])

### Summary
`addDummyInputs()` sums PSBT input and output amounts using plain JavaScript `number` arithmetic instead of a fixed-precision-safe or `BigInt` accumulator. These amounts originate from third-party/untrusted PSBT data (the same PSBTs whose derivation-path fields are explicitly treated as "potentially malicious" elsewhere in this file), and PSBT amount fields are serialized as 64-bit integers, so an attacker constructing a PSBT can set `witnessUtxo.amount` values far outside the realistic Bitcoin supply range. This is the same bug class as the Angle Protocol `changeAmount` finding: an attacker-influenced numeric value is fed into arithmetic whose safe/expected range is silently exceeded, producing incorrect results instead of reverting.

### Finding Description
`addDummyInputs` accumulates satoshi amounts with ordinary `+=` on JS `number`: [1](#0-0) 

The values come directly from `psbt.getOutputAmount(i)` and `psbt.getInputWitnessUtxo(i).amount`, both parsed off attacker-suppliable PSBT wire data. Elsewhere in the same file, comments explicitly acknowledge that "PSBTs from third parties" carry untrusted/potentially malicious pre-set fields, e.g. in `assertPsbtOnlyHasAllowedDerivationPaths`: [2](#0-1) 

PSBT amount fields are 64-bit integers (up to ~1.8×10^19), while JS `Number` only safely represents integers up to `Number.MAX_SAFE_INTEGER` (2^53−1 ≈ 9.0×10^15). A PSBT with several large, attacker-crafted `witnessUtxo.amount`/output-amount values (individually or cumulatively exceeding this threshold) will silently corrupt the running `inputAmount`/`outputAmount` totals rather than throwing, exactly mirroring the `changeAmount` report's core defect: bounded/fixed-precision arithmetic operating on an attacker-influenced value without a range check, producing a wrong numeric result instead of a safe revert.

### Impact Explanation
The computed `outputAmount > inputAmount` comparison at line 368 drives whether Exodus injects a "dummy" input and, indirectly, what amount `setInputWitnessUtxo` records for it: [3](#0-2) 

This logic exists specifically "to prevent the ledger from throwing an error w.r.t a negative fee" — i.e., it is a safety mechanism tied to fee/amount integrity during Ledger signing. If precision loss from oversized attacker-supplied amounts causes this comparison or the derived `amount = outputAmount - inputAmount` to be wrong, the dummy-input/fee-safety mechanism can be bypassed or miscalculated, potentially letting a maliciously-crafted PSBT proceed through signing with amount accounting that no longer reflects reality — undermining a hardware-wallet fee-safety check on user-signed transactions. This is a legitimate, unprivileged-user-reachable (via imported/malicious PSBT) signing-integrity issue, analogous in root cause to the reported `changeAmount` overflow (attacker-controlled value overwhelms a fixed/limited precision numeric type used in security-relevant arithmetic).

### Likelihood Explanation
Exploitation requires the attacker (dApp, PSBT file, or other third party) to supply a PSBT with extreme amount fields; the surrounding code already treats such external PSBT data as untrusted and malicious-capable (see the explicit "(potentially malicious)" comment above). No privileged access is needed — this is triggered purely by content of an imported/received PSBT that Exodus signs. However, realistic legitimate wallets rarely exceed the JS safe-integer range for Bitcoin amounts (21M BTC ≈ 2.1×10^15 sats), so triggering the miscalculation specifically requires deliberately malformed/adversarial amount fields, similar to the "edge case" characterization of the original finding.

### Recommendation
Replace the plain `number` accumulation of `outputAmount`/`inputAmount` in `addDummyInputs` with `BigInt` arithmetic (or another arbitrary/fixed-precision-safe type already used elsewhere in the codebase, e.g. `@exodus/bigint`), and validate/clamp incoming PSBT amount fields to the maximum plausible Bitcoin supply before using them in fee-safety comparisons, rejecting or safely erroring on out-of-range values rather than allowing silent precision loss.

### Proof of Concept
1. Construct a PSBT with `canModifyInputs(psbt)` returning `true` (e.g. all inputs use a non-`SIGHASH_ALL/NONE/SINGLE` sighash type).
2. Add multiple outputs and/or `witnessUtxo` amounts whose values, individually or summed, exceed `Number.MAX_SAFE_INTEGER` (2^53−1) — permitted because PSBT amount fields are 64-bit and this code performs no range validation before summation.
3. Call `addDummyInputs(psbt)`; observe that `outputAmount`/`inputAmount` (both plain JS numbers) lose precision during accumulation at [1](#0-0) , causing the `outputAmount > inputAmount` fee-safety check and the injected dummy-input amount to no longer correspond to the PSBT's true declared values.

### Citations

**File:** features/hw-ledger/src/module/assets/utils/psbt.ts (L19-38)
```typescript
export function assertPsbtOnlyHasAllowedDerivationPaths(
  psbt: PsbtV2,
  masterFingerprint: string,
  derivationPaths: string[]
) {
  for (let i = 0; i < psbt.getGlobalInputCount(); i++) {
    const BIP32_DERIVATION = 6
    const TAP_BIP32_DERIVATION = 22
    const publicKeysNormal = psbt.getInputKeyDatas(i, BIP32_DERIVATION)
    const publicKeysTap = psbt.getInputKeyDatas(i, TAP_BIP32_DERIVATION)

    // First we validate that any BIP32 derivation params that were
    // pre-assigned by a third-party (potentially malicious)
    // is actually allowed by our "derivationPaths".
    for (const publicKey of publicKeysNormal) {
      const bip32Derivation = psbt.getInputBip32Derivation(i, publicKey)
      if (bip32Derivation) {
        assertAllowedDerivation(bip32Derivation, masterFingerprint, derivationPaths)
      }
    }
```

**File:** features/hw-ledger/src/module/assets/utils/psbt.ts (L355-366)
```typescript
  let outputAmount = 0
  for (let i = 0; i < psbt.getGlobalOutputCount(); i++) {
    outputAmount += psbt.getOutputAmount(i)
  }

  let inputAmount = 0
  for (let i = 0; i < psbt.getGlobalInputCount(); i++) {
    const witnessUtxo = psbt.getInputWitnessUtxo(i)
    if (witnessUtxo) {
      inputAmount += witnessUtxo.amount
    }
  }
```

**File:** features/hw-ledger/src/module/assets/utils/psbt.ts (L368-381)
```typescript
  if (outputAmount > inputAmount) {
    // Add a dummy input to prevent the ledger from
    // throwing an error w.r.t a negative fee.
    const newInputIndex = psbt.getGlobalInputCount()
    const amount = outputAmount - inputAmount
    psbt.setGlobalInputCount(newInputIndex + 1)
    // A little easter egg, we use the very first transaction in the bitcoin
    // blockchain as the dummy input, this should make it abundantly clear
    // to external observers that this is likely not really an input.
    const FIRST_BITCOIN_TXID = '4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b'
    psbt.setInputPreviousTxId(newInputIndex, Buffer.from(FIRST_BITCOIN_TXID, 'hex'))
    psbt.setInputOutputIndex(newInputIndex, 0)
    psbt.setInputWitnessUtxo(newInputIndex, amount, Buffer.from('01', 'hex'))
  }
```
