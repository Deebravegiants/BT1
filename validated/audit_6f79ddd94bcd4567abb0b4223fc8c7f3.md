### Title
Guardrails Script Hash Not Re-Validated at Ratification/Enactment Allows Stale Proposals to Bypass the Current Constitution's Guardrails — (File: eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ratify.hs)

---

### Summary

In Conway governance, `ParameterChange` and `TreasuryWithdrawals` proposals embed a `guardrails_script_hash` that is validated against the current constitution **only at proposal submission time** (the `GOV` rule). Neither the `RATIFY` rule nor the `ENACT` rule re-checks this hash. If a `NewConstitution` action is enacted between a proposal's submission and its ratification/enactment, the pending proposal is enacted under the new constitution without ever satisfying the new constitution's guardrails script. This is the direct analog of the NFTPairWithOracle bug: a critical validation reference (the guardrails script, analogous to the oracle) is fixed at submission time and never re-verified when the underlying reference changes.

---

### Finding Description

**Submission-time check (GOV rule) — the only check that exists:**

In `conwayGovTransition`, the `GOV` rule validates the embedded `proposalPolicy` against `constitutionPolicy` (the current constitution's guardrails script hash) at the moment the proposal is submitted:

```haskell
ParameterChange _ _ proposalPolicy ->
  runTest $ checkGuardrailsScriptHash @era constitutionPolicy proposalPolicy
``` [1](#0-0) 

The guardrails script itself is also executed as a transaction witness (UTXOW) at submission time. [2](#0-1) 

**Ratification-time check (RATIFY rule) — no guardrails re-check:**

`ratifyTransition` evaluates five conditions before enacting a proposal. None of them re-check the guardrails script hash against the current (possibly updated) constitution:

```haskell
if prevActionAsExpected gas ensPrevGovActionIds
  && validCommitteeTerm govAction ensCurPParams reCurrentEpoch
  && not rsDelayed
  && withdrawalCanWithdraw govAction ensTreasury
  && acceptedByEveryone env st gas
``` [3](#0-2) 

**Enactment-time (ENACT rule) — no guardrails re-check:**

`enactmentTransition` for `ParameterChange` simply applies the parameter update with no guardrails validation:

```haskell
ParameterChange _ ppup _ ->
  st
    & ensCurPParamsL %~ (`applyPPUpdates` ppup)
    & ensPrevPParamUpdateL .~ SJust (GovPurposeId govActionId)
``` [4](#0-3) 

**The constitution change path:**

When a `NewConstitution` action is enacted, it replaces `ensConstitution` in the `EnactState`, updating the guardrails script hash for all future proposals. However, proposals already in the queue retain their original embedded `proposalPolicy` and are never re-validated:

```haskell
NewConstitution _ c ->
  st
    & ensConstitutionL .~ c
    & ensPrevConstitutionL .~ SJust (GovPurposeId govActionId)
``` [5](#0-4) 

The `GovEnv` that feeds `constitutionPolicy` into the GOV rule is derived from the current constitution at the time of the transaction: [6](#0-5) 

The `Constitution` data type stores the guardrails script hash as `constitutionGuardrailsScriptHash`: [7](#0-6) 

**Priority ordering makes the scenario structurally reachable:**

`NewConstitution` has governance priority 2, while `ParameterChange` has priority 4. When both are ratified in the same epoch, `NewConstitution` is always enacted first, guaranteeing that a co-pending `ParameterChange` is enacted under the new (changed) constitution without re-validation. [8](#0-7) 

---

### Impact Explanation

A `ParameterChange` or `TreasuryWithdrawals` proposal that was submitted and witnessed under the old constitution's guardrails script is enacted under the new constitution without the new guardrails script ever being executed. This allows:

- **Protocol parameter changes** that violate the current constitution's guardrails to

### Citations

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Gov.hs (L151-156)
```haskell
  , geEpoch :: EpochNo
  , gePParams :: PParams era
  , geGuardrailsScriptHash :: StrictMaybe ScriptHash
  , geCertState :: CertState era
  , geCommittee :: StrictMaybe (Committee era)
  }
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Gov.hs (L460-466)
```haskell
conwayGovTransition = do
  TRC
    ( GovEnv txid currentEpoch pp constitutionPolicy certState committee
      , st
      , GovSignal {gsVotingProcedures, gsProposalProcedures, gsCertificates}
      ) <-
    judgmentContext
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Gov.hs (L557-558)
```haskell
          ParameterChange _ _ proposalPolicy ->
            runTest $ checkGuardrailsScriptHash @era constitutionPolicy proposalPolicy
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ratify.hs (L334-352)
```haskell
  case rsig of
    gas@GovActionState {gasId, gasExpiresAfter} SSeq.:<| sigs -> do
      let govAction = gasAction gas
      if prevActionAsExpected gas ensPrevGovActionIds
        && validCommitteeTerm govAction ensCurPParams reCurrentEpoch
        && not rsDelayed
        && withdrawalCanWithdraw govAction ensTreasury
        && acceptedByEveryone env st gas
        then do
          newEnactState <-
            trans @(EraRule "ENACT" era) $
              TRC ((), rsEnactState, EnactSignal gasId govAction)
          let
            st' =
              st
                & rsEnactStateL .~ newEnactState
                & rsDelayedL .~ delayingAction govAction
                & rsEnactedL %~ (Seq.:|> gas)
          trans @(RATIFY era) $ TRC (env, st', RatifySignal sigs)
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Enact.hs (L89-92)
```haskell
      ParameterChange _ ppup _ ->
        st
          & ensCurPParamsL %~ (`applyPPUpdates` ppup)
          & ensPrevPParamUpdateL .~ SJust (GovPurposeId govActionId)
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Enact.hs (L112-115)
```haskell
      NewConstitution _ c ->
        st
          & ensConstitutionL .~ c
          & ensPrevConstitutionL .~ SJust (GovPurposeId govActionId)
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Governance/Procedures.hs (L949-952)
```haskell
data Constitution era = Constitution
  { constitutionAnchor :: !Anchor
  , constitutionGuardrailsScriptHash :: !(StrictMaybe ScriptHash)
  }
```
