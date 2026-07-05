### Title
`RequireGuard` Native Script Checks Guard Set Membership Without Enforcing Key Authorization - (`File: eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Scripts.hs`)

### Summary
In the Dijkstra era, `evalDijkstraNativeScript` evaluates `RequireGuard (KeyHashObj k)` by checking if `k` is present in the transaction's `guardsTxBodyL` field. It does not verify that the transaction is actually signed by the holder of key `k`. Any transaction author can include any key hash in the guards field without possessing the corresponding private key, bypassing the intended access control of the native script.

### Finding Description
The `DijkstraRequireGuard` constructor in `DijkstraNativeScriptRaw` is described in the CDDL spec as: *"A guard script requires a credential to authorize execution."* The production evaluator in `evalDijkstraNativeScript` implements this as:

```haskell
RequireGuard cred -> cred `OSet.member` guards
```

where `guards = tx ^. bodyTxL . guardsTxBodyL`. [1](#0-0) 

The `guardsTxBodyL` field is part of the transaction body and can be set to any value by the transaction author. [2](#0-1) 

The UTXOW rule for Dijkstra calls `Shelley.validateNeededWitnesses`, which computes required witnesses via `getWitsVKeyNeeded`. This function collects payment keys, stake credentials, certificate authors, and pool owners — but **not** guard credentials. [3](#0-2) [4](#0-3) 

This creates a critical asymmetry:
- **`ScriptHashObj` guards**: the script must be provided as a witness AND must validate — a real authorization check.
- **`KeyHashObj` guards**: only needs to be listed in `guardsTxBodyL` — no signature required.

The analog to the external report is exact: `onlyExecutor` checks role membership on the timelock instead of requiring `msg.sender == timelock`; `RequireGuard (KeyHashObj k)` checks set membership in `guardsTxBodyL` instead of requiring a valid signature from `k`.

### Impact Explanation
Any UTxO locked by a `RequireGuard (KeyHashObj k)` native script can be spent by any transaction that includes `k` in `guardsTxBodyL`, without possessing the private key for `k`. This enables:
- Unauthorized spending of ADA or native assets locked by such scripts
- Unauthorized minting of tokens whose policy uses `RequireGuard (KeyHashObj k)`
- Unauthorized certificate operations protected by such scripts

This matches **Critical** impact: *"Direct loss, creation, or destruction of ADA or native assets through an invalid ledger state transition."*

### Likelihood Explanation
Any unprivileged transaction sender can exploit this. The required key hash is public (embedded in the script hash on-chain). The attacker needs no special access, no leaked keys, and no privileged role — only knowledge of the key hash embedded in the script. The attack is a single transaction with `guardsTxBodyL` set to the target key hash.

### Recommendation
For `KeyHashObj` guards, add the key hash to the required witness set in the Dijkstra era's `getWitsVKeyNeeded` implementation. Specifically, when a `KeyHashObj` credential appears in `guardsTxBodyL`, it should be included in the set returned by `getWitsVKeyNeeded`, analogous to how payment key witnesses are required for spending UTxOs. For `ScriptHashObj` guards, the existing behavior (script must be provided and validate) is correct.

### Proof of Concept
The existing test in `eras/dijkstra/impl/testlib/Test/Cardano/Ledger/Dijkstra/Imp/UtxowSpec.hs` directly demonstrates the bypass:

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
``` [5](#0-4) 

The test shows that a UTxO locked by `RequireGuard guardKeyHash` is successfully spent by simply listing `guardKeyHash` in `guardsTxBodyL`, with no signature from `guardKeyHash` provided or required. The `impDijkstraSatisfyNativeScript` helper even carries a `TODO` acknowledging that `RequireGuard` is not properly satisfied: [6](#0-5) 

The root cause is in `evalDijkstraNativeScript` at line 575, which performs only a set-membership check rather than enforcing cryptographic authorization: [7](#0-6)

### Citations

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Scripts.hs (L555-576)
```haskell
evalDijkstraNativeScript ::
  (DijkstraEraScript era, NativeScript era ~ DijkstraNativeScript era) =>
  Set.Set (KeyHash Witness) ->
  ValidityInterval ->
  OSet (Credential Guard) ->
  NativeScript era ->
  Bool
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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxBody.hs (L1311-1313)
```haskell
class ConwayEraTxBody era => DijkstraEraTxBody era where
  guardsTxBodyL :: Lens' (TxBody l era) (OSet (Credential Guard))

```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxow.hs (L276-278)
```haskell
  {- witsVKeyNeeded utxo tx genDelegs ⊆ witsKeyHashes -}
  runTest $ Shelley.validateNeededWitnesses witsKeyHashes certState originalUtxo txBody

```

**File:** eras/shelley/impl/src/Cardano/Ledger/Shelley/UTxO.hs (L217-239)
```haskell
getShelleyWitsVKeyNeededNoGov ::
  EraTx era =>
  UTxO era ->
  TxBody l era ->
  Set (KeyHash Witness)
getShelleyWitsVKeyNeededNoGov utxo' txBody =
  certAuthors
    `Set.union` inputAuthors
    `Set.union` owners
    `Set.union` wdrlAuthors
  where
    inputAuthors :: Set (KeyHash Witness)
    inputAuthors = foldr' accum Set.empty (txBody ^. spendableInputsTxBodyF)
      where
        accum txin !ans =
          case txinLookup txin utxo' of
            Just txOut ->
              case txOut ^. addrTxOutL of
                Addr _ (KeyHashObj pay) _ -> Set.insert (asWitness pay) ans
                AddrBootstrap bootAddr ->
                  Set.insert (asWitness (bootstrapKeyHash bootAddr)) ans
                _ -> ans
            Nothing -> ans
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

**File:** eras/dijkstra/impl/testlib/Test/Cardano/Ledger/Dijkstra/ImpTest.hs (L153-157)
```haskell
    -- TODO: actual satisfy the native scripts by updating the transaction's guards
    ns@(RequireGuard _)
      | evalDijkstraNativeScript mempty vi guards ns -> pure $ Just mempty
      | otherwise -> pure Nothing
    _ -> error "Impossible: All NativeScripts should have been accounted for"
```
