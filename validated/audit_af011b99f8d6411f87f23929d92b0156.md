### Title
Treasury Donation Enables Targeted DoS of Governance Transactions via `currentTreasuryValue` Strict Equality Check — (File: `eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ledger.hs`)

---

### Summary

The `validateTreasuryValue` function in the Conway and Dijkstra LEDGER rules performs a **strict equality check** between the `currentTreasuryValue` field declared in a transaction body and the actual treasury value read from `chainAccountState ^. casTreasuryL`. Because any unprivileged actor can submit a transaction with a `treasuryDonation` field, an attacker can deliberately change the treasury value at the next epoch boundary, permanently invalidating any in-flight governance transaction that committed to the old treasury value. This is the direct Cardano analog of the EVM "raw balance injection" pattern: a ledger rule reads an observable quantity (`casTreasuryL`) that an external actor can manipulate, causing a derived validation to fail.

---

### Finding Description

**Root cause — `validateTreasuryValue` reads observable treasury state**

```haskell
-- eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ledger.hs
validateTreasuryValue txBody actualTreasuryValue =
  case txBody ^. currentTreasuryValueTxBodyL of
    SNothing -> pure ()
    SJust submittedTreasuryValue ->
      failureUnless (submittedTreasuryValue == actualTreasuryValue) $
        ConwayTreasuryValueMismatch
          ( Mismatch
              { mismatchSupplied = submittedTreasuryValue
              , mismatchExpected = actualTreasuryValue
              }
          )
``` [1](#0-0) 

`actualTreasuryValue` is `chainAccountState ^. casTreasuryL`, the epoch-boundary treasury value passed in from the environment. The check is a **strict equality** (`==`), so any change to the treasury — even 1 lovelace — causes the transaction to fail.

**The manipulation path — `treasuryDonation` is attacker-controlled**

Any unprivileged actor can include a `treasuryDonation` field in a transaction body. The Conway UTXO rule accumulates it into `utxosDonation`:

```haskell
-- eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Utxo.hs
updateTreasuryDonation tx utxos =
  case tx ^. isValidTxL of
    IsValid True -> utxos & utxosDonationL <>~ tx ^. bodyTxL . treasuryDonationTxBodyL
    IsValid False -> utxos
``` [2](#0-1) 

At the epoch boundary the accumulated `utxosDonation` is applied to `casTreasuryL`. From that point forward, every transaction in the new epoch that carries `currentTreasuryValue = X_old` will fail with `ConwayTreasuryValueMismatch`, because the actual treasury is now `X_old + donation`.

**The same check is present in Dijkstra**

The Dijkstra LEDGER rule calls the same `Conway.validateTreasuryValue` against the same `chainAccountState ^. casTreasuryL`:

```haskell
-- eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Ledger.hs
runTest $ Conway.validateTreasuryValue txBody (chainAccountState ^. casTreasuryL)
``` [3](#0-2) 

**Who is affected**

The `currentTreasuryValue` field is used by Plutus scripts (V3/V4) that need to reason about the treasury amount — for example, guardrails scripts that enforce a minimum treasury reserve:

```haskell
-- libs/plutus-preprocessor/src/Cardano/Ledger/Plutus/Preprocessor/Source/V3.hs
case PV3.txInfoCurrentTreasuryAmount txInfo of
  Just treasury -> treasury P.- totalWithdrawal P.>= 100_000_000
  _ -> False
``` [4](#0-3) 

Any governance proposal or parameter-change transaction that uses such a guardrails script must include `currentTreasuryValue`. These are the transactions that can be DoS'd.

**Structural parallel to the EVM report**

| EVM (`moveLiquidity`) | Cardano (`validateTreasuryValue`) |
|---|---|
| Reads `currencyToken.balanceOf(address(this))` — raw observable balance | Reads `chainAccountState ^. casTreasuryL` — raw observable treasury |
| Attacker calls `currencyToken.transfer(manager, X)` to inflate balance | Attacker submits tx with `treasuryDonation = X` to inflate treasury |
| Derived `liquidityAmount` exceeds agent-token balance → revert | Declared `currentTreasuryValue` no longer equals actual treasury → `ConwayTreasuryValueMismatch` |
| Victim: `moveLiquidity()` call fails | Victim: governance/guardrails transaction fails |

---

### Impact Explanation

**Classification:** Medium — attacker-controlled transactions modify treasury donations outside design parameters, causing governance transactions to fail.

A governance participant builds a transaction with `currentTeasuryValue = T` and a guardrails Plutus script. The attacker donates any positive amount to the treasury in the same epoch. At the epoch boundary `casTreasuryL` becomes `T + donation`. Every copy of the victim's transaction in the mempool now fails with `ConwayTreasuryValueMismatch`. The victim must rebuild and resubmit with the new treasury value — but the attacker can repeat the donation in the next epoch, sustaining the DoS indefinitely at the cost of the donated ADA (which is permanently lost to the treasury).

Governance actions that require guardrails scripts (e.g., `ParameterChange`, `TreasuryWithdrawals` with a constitution policy) are the primary targets. Blocking these actions constitutes unauthorized interference with the governance process.

---

### Likelihood Explanation

**Medium.** The attack requires:
1. The attacker to spend ADA (treasury donations are irrecoverable).
2. Correct timing — the donation must land in the same epoch as the victim's transaction.
3. Knowledge of which transactions in the mempool carry `currentTreasuryValue`.

Cardano's public mempool makes (3) trivial. The cost of (1) is a single minimum-fee transaction with 1 lovelace donation. The epoch boundary timing (2) is predictable. A well-funded attacker can sustain the DoS across multiple epochs at low cost.

---

### Recommendation

Replace the strict equality check with a check that tolerates treasury changes caused by donations accumulated in the current epoch. Concretely, the ledger could expose the pending `utxosDonation` amount and allow `submittedTreasuryValue` to equal either `casTreasuryL` (current epoch) or `casTreasuryL + utxosDonation` (projected next-epoch value). Alternatively, document that `currentTreasuryValue` is intentionally epoch-sensitive and that wallets/scripts must not rely on it for cross-epoch liveness guarantees.

---

### Proof of Concept

```
Epoch N:
  Treasury = T (casTreasuryL)

  Victim builds governance tx:
    currentTreasuryValue = T
    guardrails script checks: T - withdrawal >= MIN_RESERVE

  Attacker submits:
    treasuryDonation = 1  (costs ~0.17 ADA in fees + 1 lovelace)

Epoch N → N+1 boundary:
  utxosDonation (= 1) is applied to casTreasuryL
  New treasury = T + 1

Epoch N+1:
  Victim's tx is processed:
    validateTreasuryValue: submittedTreasuryValue (T) ≠ actualTreasuryValue (T+1)
    → FAIL: ConwayTreasuryValueMismatch { mismatchSupplied = T, mismatchExpected = T+1 }

  Victim rebuilds tx with currentTreasuryValue = T+1.
  Attacker donates 1 lovelace again.
  Cycle repeats.
```

The attacker entry path is a standard, unprivileged transaction with `treasuryDonationTxBodyL` set to any positive `Coin`. No special role, key, or governance access is required. [1](#0-0) [2](#0-1) [5](#0-4)

### Citations

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ledger.hs (L442-454)
```haskell
validateTreasuryValue ::
  ConwayEraTxBody era => TxBody l era -> Coin -> Test (ConwayLedgerPredFailure era)
validateTreasuryValue txBody actualTreasuryValue =
  case txBody ^. currentTreasuryValueTxBodyL of
    SNothing -> pure ()
    SJust submittedTreasuryValue ->
      failureUnless (submittedTreasuryValue == actualTreasuryValue) $
        ConwayTreasuryValueMismatch
          ( Mismatch
              { mismatchSupplied = submittedTreasuryValue
              , mismatchExpected = actualTreasuryValue
              }
          )
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Utxo.hs (L200-209)
```haskell
-- | Accumulate treasury donation for valid transactions
updateTreasuryDonation ::
  (AlonzoEraTx era, ConwayEraTxBody era) =>
  Tx TopTx era ->
  UTxOState era ->
  UTxOState era
updateTreasuryDonation tx utxos =
  case tx ^. isValidTxL of
    IsValid True -> utxos & utxosDonationL <>~ tx ^. bodyTxL . treasuryDonationTxBodyL
    IsValid False -> utxos
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Ledger.hs (L388-392)
```haskell
    if tx ^. isValidTxL == IsValid True
      then do
        let txBody = tx ^. bodyTxL
        runTest $ Conway.validateTreasuryValue txBody (chainAccountState ^. casTreasuryL)
        runTest $ validateAllRefScriptSize pp originalUtxo tx
```

**File:** libs/plutus-preprocessor/src/Cardano/Ledger/Plutus/Preprocessor/Source/V3.hs (L244-246)
```haskell
                case PV3D.txInfoCurrentTreasuryAmount txInfo of
                  Just treasury -> treasury P.- totalWithdrawal P.>= 100_000_000
                  _ -> False
```
