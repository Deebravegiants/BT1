### Title
`RequireGuard` Key-Hash Credentials Not Enforced as Witnesses — Guard Mechanism Exists but Enforcement Is Missing - (File: `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Scripts.hs`)

### Summary

The Dijkstra era introduces a new `RequireGuard` native script constructor that is supposed to require a credential to authorize script execution. For key-hash credentials, `evalDijkstraNativeScript` only checks that the credential is *listed* in the transaction's `guardsTxBodyL` field, but the ledger rules never require a corresponding VKey signature from that key hash. Any transaction author can satisfy a `RequireGuard (KeyHashObj kh)` script by simply inserting `kh` into `guardsTxBodyL` without possessing the private key for `kh`. This is the direct Cardano Ledger analog of the `PhiNFT1155` bug: the guard mechanism is present and wired into script evaluation, but the enforcement hook (requiring a witness) is never connected.

### Finding Description

**Root cause — `evalDijkstraNativeScript` only checks set membership:**

```haskell
-- Scripts.hs line 575
RequireGuard cred -> cred `OSet.member` guards
```

`guards` is the `OSet (Credential Guard)` drawn from the transaction body's `guardsTxBodyL`. For a `KeyHashObj kh` credential this reduces to: "is `kh` present in the guards list?" — nothing more. [1](#0-0) 

**Missing enforcement — `getDijkstraScriptsNeeded` silently drops key-hash guards:**

```haskell
-- UTxO.hs lines 173-176
guardingScriptsNeeded = AlonzoScriptsNeeded $
  catMaybes $
    zipAsIxItem (txb ^. guardsTxBodyL) $
      \(AsIxItem idx cred) ->
        (\sh -> (GuardingPurpose (AsIxItem idx sh), sh)) <$> credScriptHash cred
```

`credScriptHash` returns `Nothing` for `KeyHashObj` credentials, so key-hash guards are silently excluded from `scriptsNeeded`. They are therefore never passed to `validateFailedBabbageScripts` and never validated. [2](#0-1) 

**Missing enforcement — `validateNeededWitnesses` never sees key-hash guards:**

The UTXOW transition calls `Shelley.validateNeededWitnesses witsKeyHashes certState originalUtxo txBody`, which is backed by `getConwayWitsVKeyNeeded`. That function derives required witnesses from spending inputs, withdrawals, certificates, and governance actions — not from `guardsTxBodyL`. Key-hash guard credentials are therefore never added to the required-witness set. [3](#0-2) 

**Contrast with script-hash guards (which ARE enforced):**

Script-hash credentials in `guardsTxBodyL` are added to `scriptsNeeded` via `GuardingPurpose`, so `validateFailedBabbageScripts` runs them through `validateNativeScript`. Key-hash credentials receive no analogous treatment. [4](#0-3) 

**Test framework confirms the gap:**

The test helper `impDijkstraSatisfyNativeScript` explicitly returns `pure $ Just mempty` (no key pairs) for `RequireGuard` and carries a `TODO` comment acknowledging that guard satisfaction is not yet implemented. The passing test `"Spending inputs locked by script requiring a keyhash guard"` succeeds because the framework adds the guard to `guardsTxBodyL` but adds *no* signature from that key hash — and the ledger accepts it. [5](#0-4) [6](#0-5) 

**Exploit path (top-level transaction):**

1. Victim locks a UTxO with a script `RequireGuard (KeyHashObj victimKH)`.
2. Attacker constructs a transaction spending that UTxO.
3. Attacker sets `guardsTxBodyL = [KeyHashObj victimKH]` — no private key for `victimKH` needed.
4. `evalDijkstraNativeScript` evaluates `RequireGuard (KeyHashObj victimKH)` → `victimKH \`OSet.member\` guards` → `True`.
5. `validateFailedBabbageScripts` does not flag the script (key-hash guards are not in `scriptsNeeded`).
6. `validateNeededWitnesses` does not require a signature from `victimKH`.
7. Transaction is accepted; UTxO is spent without the victim's authorization.

The same path applies to minting policies and certificates protected by `RequireGuard (KeyHashObj …)`.

### Impact Explanation

**Critical — Direct loss of ADA or native assets through an invalid ledger state transition.**

Any UTxO, minting policy, or certificate locked by a `RequireGuard (KeyHashObj kh)` script can be spent/executed by an unprivileged attacker who does not hold the private key for `kh`. The attacker only needs to craft a transaction body that lists `kh` in `guardsTxBodyL`. No privileged access, no leaked key, and no consensus majority is required.

### Likelihood Explanation

High. The attack requires only the ability to submit a valid transaction — the baseline capability of any Cardano user. The attacker needs to know the target key hash (publicly derivable from the UTxO's script hash and the script itself) and to set one field in the transaction body. No brute-force or cryptographic work is involved.

### Recommendation

Key-hash credentials listed in `guardsTxBodyL` must be added to the required-witness set, analogously to how spending inputs locked by key-hash addresses are handled. Concretely:

1. In `getDijkstraScriptsNeeded` (or a companion function), extract `KeyHashObj kh` entries from `guardsTxBodyL` and add them to the set of required VKey witnesses — either by extending `getConwayWitsVKeyNeeded` or by adding a dedicated check in `dijkstraUtxowTransition`.
2. Add a `runTest` in `dijkstraUtxowTransition` that verifies every `KeyHashObj kh` in `guardsTxBodyL` has a corresponding entry in `witsKeyHashes`.
3. Mirror the same fix in `dijkstraSubUtxowTransition` for subtransaction-level guards.
4. Update `impDijkstraSatisfyNativeScript` to resolve the `TODO` and automatically provide the required key pair when satisfying a `RequireGuard (KeyHashObj _)` script.

### Proof of Concept

The existing test `"Spending inputs locked by script requiring a keyhash guard"` already demonstrates the bug: it submits a transaction with `guardsTxBodyL = [guardKeyHash]` and no signature from `guardKeyHash`, and `submitTx_` succeeds. To make the exploit explicit, replace `freshKeyHash` with any externally known key hash (e.g., one belonging to a victim) and observe that the transaction is still accepted without the victim's signature. [6](#0-5) [7](#0-6) [4](#0-3)

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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs (L166-177)
```haskell
getDijkstraScriptsNeeded ::
  (DijkstraEraTxBody era, DijkstraEraScript era) =>
  UTxO era -> TxBody l era -> AlonzoScriptsNeeded era
getDijkstraScriptsNeeded utxo txb =
  getConwayScriptsNeeded utxo txb
    <> guardingScriptsNeeded
  where
    guardingScriptsNeeded = AlonzoScriptsNeeded $
      catMaybes $
        zipAsIxItem (txb ^. guardsTxBodyL) $
          \(AsIxItem idx cred) -> (\sh -> (GuardingPurpose (AsIxItem idx sh), sh)) <$> credScriptHash cred

```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxow.hs (L276-278)
```haskell
  {- witsVKeyNeeded utxo tx genDelegs ⊆ witsKeyHashes -}
  runTest $ Shelley.validateNeededWitnesses witsKeyHashes certState originalUtxo txBody

```

**File:** eras/dijkstra/impl/testlib/Test/Cardano/Ledger/Dijkstra/ImpTest.hs (L153-157)
```haskell
    -- TODO: actual satisfy the native scripts by updating the transaction's guards
    ns@(RequireGuard _)
      | evalDijkstraNativeScript mempty vi guards ns -> pure $ Just mempty
      | otherwise -> pure Nothing
    _ -> error "Impossible: All NativeScripts should have been accounted for"
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
