### Title
`RequireGuard (KeyHashObj kh)` Native Scripts Bypassable Without Key Authorization — (`File: eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs`)

---

### Summary

In the Dijkstra era, the new `RequireGuard` native script variant is intended to require that a specific credential authorizes script execution. When the credential is a `ScriptHashObj`, the script witness is properly required and validated. However, when the credential is a `KeyHashObj`, the corresponding key hash is **never required as a VKey witness**. Any transaction can satisfy `RequireGuard (KeyHashObj kh)` by simply including `kh` in the `guardsTxBodyL` field of the transaction body — without possessing the private key for `kh`. This is a direct analog to the ERC20/points-program inconsistency: one code path (`getDijkstraScriptsNeeded`) correctly distinguishes credential types, while the VKey-witness path (`getConwayWitsVKeyNeeded`) is never extended to cover key-hash guards.

---

### Finding Description

The Dijkstra era introduces `guardsTxBodyL :: OSet (Credential Guard)` in the transaction body and a new native script constructor `RequireGuard (Credential Guard)`. The script evaluator checks:

```haskell
RequireGuard cred -> cred `OSet.member` guards
```

where `guards` is taken directly from `txBody ^. guardsTxBodyL`. [1](#0-0) 

The `getDijkstraScriptsNeeded` function correctly distinguishes credential types: it uses `credScriptHash cred` to extract only `ScriptHashObj` credentials and adds them to `scriptsNeeded` (with a `GuardingPurpose` tag). `KeyHashObj` credentials return `Nothing` from `credScriptHash` and are silently dropped via `catMaybes`. [2](#0-1) 

Script-hash guards are therefore properly required to be witnessed (via `babbageMissingScripts`) and validated (via `validateFailedBabbageScripts`).

However, the `EraUTxO` instance for `DijkstraEra` delegates VKey-witness collection to the unmodified Conway function:

```haskell
getWitsVKeyNeeded _ = getConwayWitsVKeyNeeded
``` [3](#0-2) 

`getConwayWitsVKeyNeeded` predates `guardsTxBodyL` and has no knowledge of it. It never inspects `guardsTxBodyL` for `KeyHashObj` credentials. The Dijkstra UTXOW transition rule adds no compensating check: [4](#0-3) 

The only guard-related check in the UTXOW rule verifies that sub-transaction required guards are present in the top-level `guardsTxBodyL` — it does not verify that any key-hash guard is authorized by a VKey signature: [5](#0-4) 

The result: a `KeyHashObj kh` placed in `guardsTxBodyL` satisfies `RequireGuard (KeyHashObj kh)` unconditionally, because the ledger never checks that the transaction is signed by `kh`.

---

### Impact Explanation

**Critical — Direct loss of ADA or native assets through an invalid ledger state transition.**

Any UTxO locked by a `RequireGuard (KeyHashObj kh)` native script can be spent by an unprivileged attacker. The attacker constructs a transaction that:

1. Spends the target UTxO (whose payment credential hashes to the `RequireGuard` script).
2. Includes `KeyHashObj kh` in `guardsTxBodyL`.
3. Provides no VKey witness for `kh`.

The ledger accepts this transaction because:
- `getDijkstraScriptsNeeded` does not add `kh` to `scriptsNeeded` (it is a key hash, not a script hash).
- `getConwayWitsVKeyNeeded` does not add `kh` to required VKey witnesses (it does not inspect `guardsTxBodyL`).
- `evalDijkstraNativeScript` evaluates `RequireGuard (KeyHashObj kh)` as `True` because `kh` is in `guards`.
- No other check in `dijkstraUtxowTransition` requires `kh` to be witnessed.

The attacker gains full control of the locked value without authorization.

---

### Likelihood Explanation

**High.** The attack requires no special privilege, no governance majority, and no key material beyond knowledge of the target key hash (which is public). The attacker only needs to craft a transaction body containing the target key hash in `guardsTxBodyL`. The Dijkstra era is the only era where `RequireGuard` exists, so the attack surface is bounded to that era, but within it the bypass is unconditional.

---

### Recommendation

Override `getWitsVKeyNeeded` in the `EraUTxO DijkstraEra` instance to extend `getConwayWitsVKeyNeeded` with the key-hash credentials present in `guardsTxBodyL`:

```haskell
getWitsVKeyNeeded certState utxo txBody =
  getConwayWitsVKeyNeeded certState utxo txBody
    <> Set.fromList
         [ kh
         | KeyHashObj kh <- OSet.toList (txBody ^. guardsTxBodyL)
         ]
```

This mirrors the pattern already used in `getDijkstraScriptsNeeded`, which handles `ScriptHashObj` guards, ensuring both credential kinds are consistently enforced.

---

### Proof of Concept

**Setup:** Deploy a UTxO locked by `RequireGuard (KeyHashObj aliceKH)` where `aliceKH` is Alice's staking key hash.

**Attack:**

```haskell
-- Attacker does NOT have Alice's private key.
-- Attacker knows aliceKH (public information).
let attackTx =
      mkBasicTx
        ( mkBasicTxBody
            & inputsTxBodyL  .~ [aliceLockedTxIn]   -- UTxO locked by RequireGuard
            & outputsTxBodyL .~ [attackerOutput]
        )
        & bodyTxL . guardsTxBodyL .~ [KeyHashObj aliceKH]
        -- No VKey witness for aliceKH is added.
```

**Ledger evaluation:**

1. `getDijkstraScriptsNeeded`: `credScriptHash (KeyHashObj aliceKH) = Nothing` → `aliceKH` not in `scriptsNeeded`. [6](#0-5) 
2. `getConwayWitsVKeyNeeded`: does not inspect `guardsTxBodyL` → `aliceKH` not in required VKey witnesses. [3](#0-2) 
3. `evalDijkstraNativeScript`: `RequireGuard (KeyHashObj aliceKH) → KeyHashObj aliceKH `OSet.member` guards = True`. [7](#0-6) 
4. All UTXOW checks pass. Transaction is accepted. Attacker receives Alice's funds.

### Citations

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Scripts.hs (L568-576)
```haskell
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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs (L139-139)
```haskell
  getWitsVKeyNeeded _ = getConwayWitsVKeyNeeded
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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxow.hs (L272-277)
```haskell
  -- check VKey witnesses
  {- ∀ (vk ↦ σ) ∈ (txwitsVKey txw), V_vk⟦ txbodyHash ⟧_σ -}
  runTestOnSignal $ Shelley.validateVerifiedWits tx

  {- witsVKeyNeeded utxo tx genDelegs ⊆ witsKeyHashes -}
  runTest $ Shelley.validateNeededWitnesses witsKeyHashes certState originalUtxo txBody
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxow.hs (L292-297)
```haskell
  {- concatMapˡ (λ txSub → mapˢ proj₁ (TopLevelGuardsOf txSub)) (SubTransactionsOf txTop) ⊆ GuardsOf txTop -}
  let requiredGuardsBySubTxs =
        foldMap (Map.keysSet . (^. bodyTxL . requiredTopLevelGuardsL)) subTxs
      topLevelGuards = OSet.toSet (txBody ^. guardsTxBodyL)
      missingGuards = requiredGuardsBySubTxs `Set.difference` topLevelGuards
  runTestOnSignal $ failureOnNonEmptySet missingGuards MissingRequiredGuards
```
