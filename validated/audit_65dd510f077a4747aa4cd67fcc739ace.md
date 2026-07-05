### Title
`RequireGuard (KeyHashObj kh)` Native Script Bypass via Unsigned Guard Declaration — (`File: eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Scripts.hs`)

### Summary

In the Dijkstra era, the new `RequireGuard` native script constructor is meant to require a credential to authorize script execution. However, when the credential is a `KeyHashObj kh` (a key hash), the ledger only checks that the key hash appears in the transaction body's `guards` field — it never verifies that the corresponding private key actually signed the transaction. Any unprivileged transaction author can add an arbitrary key hash to the `guards` field without possessing the private key, trivially satisfying any `RequireGuard (KeyHashObj kh)` script. This is the direct analog of the hPAL "PAL Locker" bypass: a restriction mechanism intended to require authorization from a specific party can be circumvented by any third party through a simple self-declaration.

---

### Finding Description

The Dijkstra era introduces `DijkstraRequireGuard (Credential Guard)` as a seventh variant of the native script language. Its evaluation is defined in `evalDijkstraNativeScript`:

```haskell
RequireGuard cred -> cred `OSet.member` guards
```

where `guards` is read directly from `txBody ^. guardsTxBodyL` — a field the transaction author populates freely. [1](#0-0) 

The `guards` field is declared in `DijkstraTxBodyRaw` as `dtbrGuards :: !(OSet (Credential Guard))` for top-level transactions and `dstbrGuards :: !(OSet (Credential Guard))` for sub-transactions. [2](#0-1) 

The UTXOW transition rule (`dijkstraUtxowTransition`) performs the following checks relevant to guards:

1. **Phase-1 script validation** (`validateFailedBabbageScripts`) — runs `evalDijkstraNativeScript`, which checks `cred `OSet.member` guards`. For `KeyHashObj kh`, this passes as long as `kh` is listed in the guards set.
2. **Missing scripts** (`babbageMissingScripts`) — ensures script witnesses are provided for `ScriptHashObj` guards.
3. **Needed witnesses** (`validateNeededWitnesses`) — checks that key witnesses required by UTxO inputs, certificates, and withdrawals are present. **The `guards` field is not consulted here.** [3](#0-2) 

There is a critical asymmetry:

| Guard credential type | Script witness required? | Signature required? |
|---|---|---|
| `ScriptHashObj sh` | Yes — `babbageMissingScripts` enforces it | Yes — script must validate |
| `KeyHashObj kh` | N/A | **No — nothing checks this** |

For `ScriptHashObj sh` guards, the script must be provided as a witness and must pass validation. For `KeyHashObj kh` guards, no corresponding check exists. The CDDL specification comments: *"A guard script requires a credential to authorize execution"*, but for key-hash credentials this authorization is never enforced. [4](#0-3) 

This is confirmed by the existing test suite, which explicitly demonstrates that a UTxO locked by `RequireGuard (KeyHashObj kh)` is spendable by adding `kh` to the guards field **without any signature from `kh`**:

```haskell
submitTx_ $ tx & bodyTxL . guardsTxBodyL .~ [guardKeyHash]
-- No signature for guardKeyHash is provided or required
``` [5](#0-4) 

---

### Impact Explanation

Any UTxO locked by a native script containing `RequireGuard (KeyHashObj kh)` — or any minting policy, certificate, or governance action gated by such a script — can be unilaterally authorized by any transaction author who simply lists `kh` in the `guards` field. No private key is needed. This enables:

- **Direct theft of ADA and native assets**: UTxOs locked by `RequireGuard (KeyHashObj kh)` scripts are spendable by anyone.
- **Unauthorized minting**: Minting policies using `RequireGuard (KeyHashObj kh)` can be bypassed, allowing unlimited token creation or destruction.
- **Unauthorized governance/certificate actions**: Any script-gated certificate or governance action using this pattern is unprotected.

This matches the **Critical** impact category: *direct loss, creation, or destruction of ADA or native assets through an invalid ledger state transition*.

---

### Likelihood Explanation

The `RequireGuard` constructor is new in Dijkstra era and is documented as requiring a credential to authorize execution. Script authors who use `RequireGuard (KeyHashObj kh)` will naturally expect behavior analogous to `RequireSignature kh` — i.e., that the key must sign the transaction. The inconsistency between `ScriptHashObj` guards (which are fully validated) and `KeyHashObj` guards (which are not) is non-obvious and not documented. Any script author who uses `RequireGuard (KeyHashObj kh)` to protect funds will unknowingly deploy a script with no effective access control. The attack requires no special privileges — any transaction submitter can exploit it.

---

### Recommendation

For `KeyHashObj kh` credentials in the `guards` field that are actually consumed by a `RequireGuard` script check, the UTXOW rule must require that `kh` appears in the set of verified key witnesses (`witsKeyHashes`). Concretely, the `dijkstraUtxowTransition` should collect all `KeyHashObj kh` credentials from the `guards` set that are referenced by any evaluated `RequireGuard` script, and verify each `kh` is present in `witsKeyHashes` — mirroring the existing `RequireSignature` enforcement path. Alternatively, the `witsVKeyNeeded` function should be extended to include key-hash guards that are referenced by scripts needing validation.

---

### Proof of Concept

1. Alice deploys a UTxO locked by native script `S = RequireGuard (KeyHashObj kh_bob)`, intending that only Bob (holder of `kh_bob`'s private key) can spend it.
2. Mallory constructs a transaction spending Alice's UTxO:
   - Sets `inputs = {alice_utxo}`
   - Sets `guards = {KeyHashObj kh_bob}` in the transaction body
   - Provides script `S` as a witness
   - Does **not** provide a signature from `kh_bob`
3. The ledger evaluates `RequireGuard (KeyHashObj kh_bob)` → `KeyHashObj kh_bob `OSet.member` {KeyHashObj kh_bob}` → `True`.
4. `validateNeededWitnesses` does not check the `guards` field, so no signature for `kh_bob` is required.
5. The transaction is accepted. Mallory steals Alice's funds without Bob's key.

The root cause is at: [6](#0-5) 

with the missing enforcement in: [7](#0-6)

### Citations

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Scripts.hs (L562-576)
```haskell
evalDijkstraNativeScript keyHashes (ValidityInterval txStart txExp) guards = go
  where
    -- the evaluation will stop as soon as it reaches the required number of valid scripts
    isValidMOf n SSeq.Empty = n <= 0
    isValidMOf n (ts SSeq.:<| tss) =
      n <= 0 || if go ts then isValidMOf (n - 1) tss else isValidMOf n tss
    go = \case
      RequireTimeStart lockStart -> lockStart `lteNegInfty` txStart
      RequireTimeExpire lockExp -> txExp `ltePosInfty` lockExp
      RequireSignature hash -> hash `Set.member` keyHashes
      RequireAllOf xs -> all go xs
      RequireAnyOf xs -> any go xs
      RequireMOf m xs -> isValidMOf m xs
      RequireGuard cred -> cred `OSet.member` guards
      _ -> error "Impossible: All NativeScripts should have been accounted for"
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxBody.hs (L163-209)
```haskell
data DijkstraTxBodyRaw l era where
  DijkstraTxBodyRaw ::
    { dtbrSpendInputs :: !(Set TxIn)
    , dtbrCollateralInputs :: !(Set TxIn)
    , dtbrReferenceInputs :: !(Set TxIn)
    , dtbrOutputs :: !(StrictSeq (Sized (TxOut era)))
    , dtbrCollateralReturn :: !(StrictMaybe (Sized (TxOut era)))
    , dtbrTotalCollateral :: !(StrictMaybe Coin)
    , dtbrCerts :: !(OSet.OSet (TxCert era))
    , dtbrWithdrawals :: !Withdrawals
    , dtbrFee :: !Coin
    , dtbrVldt :: !ValidityInterval
    , dtbrGuards :: !(OSet (Credential Guard))
    , dtbrMint :: !MultiAsset
    , dtbrScriptIntegrityHash :: !(StrictMaybe ScriptIntegrityHash)
    , dtbrAuxDataHash :: !(StrictMaybe TxAuxDataHash)
    , dtbrNetworkId :: !(StrictMaybe Network)
    , dtbrVotingProcedures :: !(VotingProcedures era)
    , dtbrProposalProcedures :: !(OSet.OSet (ProposalProcedure era))
    , dtbrCurrentTreasuryValue :: !(StrictMaybe Coin)
    , dtbrTreasuryDonation :: !Coin
    , dtbrSubTransactions :: !(OMap TxId (Tx SubTx era))
    , dtbrDirectDeposits :: !DirectDeposits
    , dtbrAccountBalanceIntervals :: !(AccountBalanceIntervals era)
    } ->
    DijkstraTxBodyRaw TopTx era
  DijkstraSubTxBodyRaw ::
    { dstbrSpendInputs :: !(Set TxIn)
    , dstbrReferenceInputs :: !(Set TxIn)
    , dstbrOutputs :: !(StrictSeq (Sized (TxOut era)))
    , dstbrCerts :: !(OSet.OSet (TxCert era))
    , dstbrWithdrawals :: !Withdrawals
    , dstbrVldt :: !ValidityInterval
    , dstbrGuards :: !(OSet (Credential Guard))
    , dstbrMint :: !MultiAsset
    , dstbrScriptIntegrityHash :: !(StrictMaybe ScriptIntegrityHash)
    , dstbrAuxDataHash :: !(StrictMaybe TxAuxDataHash)
    , dstbrNetworkId :: !(StrictMaybe Network)
    , dstbrVotingProcedures :: !(VotingProcedures era)
    , dstbrProposalProcedures :: !(OSet.OSet (ProposalProcedure era))
    , dstbrCurrentTreasuryValue :: !(StrictMaybe Coin)
    , dstbrTreasuryDonation :: !Coin
    , dstbrRequiredTopLevelGuards :: !(Map (Credential Guard) (StrictMaybe (Data era)))
    , dstbrDirectDeposits :: !DirectDeposits
    , dstbrAccountBalanceIntervals :: !(AccountBalanceIntervals era)
    } ->
    DijkstraTxBodyRaw SubTx era
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxow.hs (L242-297)
```haskell
  {- ∀s ∈ (txscripts txw utxo neededHashes ) ∩ Scriptph1 , validateScript s tx -}
  -- Per-level: phase-1 script validation is per-tx (script execution)
  runTest $ Babbage.validateFailedBabbageScripts tx scriptsProvided topScriptHashesNeeded

  {- neededHashes − dom(refScripts tx utxo) = dom(txwitscripts txw) -}
  -- Aggregated: missing/extraneous scripts across all levels.
  let witnessScripts =
        Map.keysSet (tx ^. witsTxL . scriptTxWitsL)
          <> foldMap (Map.keysSet . (^. witsTxL . scriptTxWitsL)) subTxs
      allRefScriptInputs =
        txBody ^. referenceInputsTxBodyL
          <> txBody ^. inputsTxBodyL
          <> foldMap
            ( \subTx ->
                subTx ^. bodyTxL . referenceInputsTxBodyL
                  <> subTx ^. bodyTxL . inputsTxBodyL
            )
            subTxs
      refScripts = Map.keysSet $ getReferenceScripts originalUtxo allRefScriptInputs
  runTest $ Babbage.babbageMissingScripts pp allScriptHashesNeeded refScripts witnessScripts

  {-  inputHashes ⊆  dom(txdats txw) ⊆  allowed -}
  -- Per-level: datum check for top-level tx's own spend inputs
  runTest $ Alonzo.missingRequiredDatums scriptsProvided originalUtxo tx

  {- dom (txrdmrs tx) = { rdptr txb sp | (sp, h) ∈ scriptsNeeded utxo tx,
                          h ↦ s ∈ txscripts txw, s ∈ Scriptph2} -}
  -- Per-level: redeemer indexing is per-tx
  runTest $ Alonzo.hasExactSetOfRedeemers tx scriptsProvided topScriptsNeeded

  -- check VKey witnesses
  {- ∀ (vk ↦ σ) ∈ (txwitsVKey txw), V_vk⟦ txbodyHash ⟧_σ -}
  runTestOnSignal $ Shelley.validateVerifiedWits tx

  {- witsVKeyNeeded utxo tx genDelegs ⊆ witsKeyHashes -}
  runTest $ Shelley.validateNeededWitnesses witsKeyHashes certState originalUtxo txBody

  -- check metadata hash
  {- ((adh = ◇) ∧ (ad= ◇)) ∨ (adh = hashAD ad) -}
  runTestOnSignal $ Shelley.validateMetadata pp tx

  {- ∀x ∈ range(txdats txw) ∪ range(txwitscripts txw) ∪ (⋃ ( , ,d,s) ∈ txouts tx {s, d}),
                       x ∈ Script ∪ Datum ⇒ isWellFormed x -}
  runTest $ Babbage.validateScriptsWellFormed pp tx

  {- scriptIntegrityHash txb = hashScriptIntegrity pp (languages txw) (txrdmrs txw) -}
  -- Per-level: script integrity is per-tx (depends on that tx's redeemers and language views)
  let scriptIntegrity = mkScriptIntegrity pp tx (plutusLanguagesUsedStAnnTx stAnnTx)
  runTest $ Alonzo.checkScriptIntegrityHash tx pp scriptIntegrity

  {- concatMapˡ (λ txSub → mapˢ proj₁ (TopLevelGuardsOf txSub)) (SubTransactionsOf txTop) ⊆ GuardsOf txTop -}
  let requiredGuardsBySubTxs =
        foldMap (Map.keysSet . (^. bodyTxL . requiredTopLevelGuardsL)) subTxs
      topLevelGuards = OSet.toSet (txBody ^. guardsTxBodyL)
      missingGuards = requiredGuardsBySubTxs `Set.difference` topLevelGuards
  runTestOnSignal $ failureOnNonEmptySet missingGuards MissingRequiredGuards
```

**File:** eras/dijkstra/impl/cddl/data/dijkstra.cddl (L426-429)
```text
; Dijkstra adds guard scripts for enhanced security.
; A guard script requires a credential to authorize execution.
script_require_guard = (6, credential)

```

**File:** eras/dijkstra/impl/testlib/Test/Cardano/Ledger/Dijkstra/Imp/UtxowSpec.hs (L30-38)
```haskell
    it "Spending inputs locked by script requiring a keyhash guard" $ do
      guardKeyHash <- KeyHashObj <$> freshKeyHash
      scriptHash <- impAddNativeScript (RequireGuard guardKeyHash)
      txIn <- produceScript scriptHash
      let tx = mkBasicTx (mkBasicTxBody & inputsTxBodyL .~ [txIn])
      submitFailingTx
        tx
        [injectFailure $ Conway.ScriptWitnessNotValidatingUTXOW $ NES.singleton scriptHash]
      submitTx_ $ tx & bodyTxL . guardsTxBodyL .~ [guardKeyHash]
```
