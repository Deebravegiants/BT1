### Title
Unauthenticated `guards` Field Allows Bypassing `RequireGuard` Script Authorization - (File: `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxow.hs`)

---

### Summary

The Dijkstra era introduces a `guards` field in transaction bodies and a `RequireGuard` native script constructor. The `guards` field is not authenticated: any transaction author can populate it with arbitrary credentials without providing witnesses for those credentials. Because `RequireGuard cred` scripts pass solely by checking membership in the `guards` set, an unprivileged sender can satisfy any `RequireGuard`-locked UTxO or minting policy without controlling the required credential.

---

### Finding Description

**New Dijkstra primitives:**

1. `guardsTxBodyL` — an `OSet (Credential Guard)` in every transaction body (top-level and sub-transaction).
2. `DijkstraRequireGuard cred` — a new native-script constructor that evaluates to `True` iff `cred ∈ guards` of the validating transaction.
3. `requiredTopLevelGuardsL` — a `Map (Credential Guard) (StrictMaybe (Data era))` in sub-transaction bodies, declaring which credentials must appear in the enclosing top-level transaction's `guards` set.

**The authorization gap:**

The Dijkstra UTXOW transition (`dijkstraUtxowTransition`) performs the following guard-related check:

```haskell
-- eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxow.hs:292-297
let requiredGuardsBySubTxs =
      foldMap (Map.keysSet . (^. bodyTxL . requiredTopLevelGuardsL)) subTxs
    topLevelGuards = OSet.toSet (txBody ^. guardsTxBodyL)
    missingGuards = requiredGuardsBySubTxs `Set.difference` topLevelGuards
runTestOnSignal $ failureOnNonEmptySet missingGuards MissingRequiredGuards
```

This only verifies that the top-level `guards` set *contains* every credential demanded by sub-transactions. It does **not** verify that the transaction author is *authorized* to assert those credentials.

The witness check immediately above it is:

```haskell
-- eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxow.hs:277
runTest $ Shelley.validateNeededWitnesses witsKeyHashes certState originalUtxo txBody
```

`Shelley.validateNeededWitnesses` computes required key-hash witnesses from UTxO payment keys, withdrawal stake credentials, certificate credentials, and pool-owner keys. The `guards` field is **absent** from this computation. No analogous script-witness check for guard credentials exists in the rule either.

The native-script evaluator confirms the one-sided check:

```haskell
-- eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Scripts.hs:575
RequireGuard cred -> cred `OSet.member` guards
```

Satisfaction depends entirely on set membership; no signature or script execution is required for the credential itself.

**Result:** a transaction author can write any set of credentials into `guardsTxBodyL` without supplying witnesses for them. Every `RequireGuard cred` script whose `cred` appears in that set will evaluate to `True`.

---

### Impact Explanation

**Critical — Direct loss or creation of native assets through an invalid ledger state transition.**

- **UTxO theft:** Any UTxO locked by a `RequireGuard cred` address script can be spent by an attacker who simply lists `cred` in their transaction's `guards` field, with no signature or script from the actual credential holder.
- **Unauthorized minting/burning:** Any native-asset minting policy that uses `RequireGuard cred` can be satisfied the same way, allowing arbitrary minting or burning of tokens without the policy author's consent.
- **Sub-transaction authorization bypass:** The `requiredTopLevelGuards` mechanism is intended to let sub-transaction authors demand that specific principals co-authorize the enclosing transaction. Because the top-level author can freely populate `guards`, this co-authorization requirement is entirely circumventable.

---

### Likelihood Explanation

The entry path requires only the ability to submit a valid Dijkstra-era transaction — no privileged keys, no governance role, no stake. Any unprivileged sender can craft a transaction body with an arbitrary `guards` set. The only prerequisite is that the target UTxO or minting policy uses a `RequireGuard`-based script, which is the intended use-case for the new primitive.

---

### Recommendation

Credentials listed in `guardsTxBodyL` must be witnessed in the same way as other credential-bearing fields:

- **Key-hash guard credentials** (`KeyHashObj kh`): require a VKey witness from `kh` (extend `witsVKeyNeeded` / `getDijkstraWitsVKeyNeeded` to include `Map.keysSet (txBody ^. guardsTxBodyL)` filtered to key-hash credentials).
- **Script-hash guard credentials** (`ScriptHashObj sh`): require the script `sh` to be provided and to validate (extend `scriptsNeeded` to include guard script hashes).

The `validateNeededWitnesses` call in `dijkstraUtxowTransition` and the analogous call in `dijkstraSubUtxowTransition` must both be updated to enforce these requirements.

---

### Proof of Concept

1. Alice deploys a UTxO at an address whose payment script is `RequireGuard aliceCred` (where `aliceCred = KeyHashObj aliceKH`).
2. Bob constructs a transaction that:
   - spends Alice's UTxO as an input,
   - sets `guardsTxBodyL = OSet.singleton aliceCred` in the transaction body,
   - provides **no** witness for `aliceKH`.
3. `dijkstraUtxowTransition` calls `validateNeededWitnesses`; `aliceCred` is not in the computed needed-witness set, so no witness is demanded.
4. `validateFailedBabbageScripts` evaluates the `RequireGuard aliceCred` script: `aliceCred ∈ guards` → `True`.
5. The transaction is accepted; Bob has stolen Alice's funds without her authorization. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 
<cite repo="Linkmegit/cardano-ledger--019" path="eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubUtxow.hs" start="260" end="

### Citations

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxow.hs (L272-278)
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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Scripts.hs (L571-576)
```haskell
      RequireSignature hash -> hash `Set.member` keyHashes
      RequireAllOf xs -> all go xs
      RequireAnyOf xs -> any go xs
      RequireMOf m xs -> isValidMOf m xs
      RequireGuard cred -> cred `OSet.member` guards
      _ -> error "Impossible: All NativeScripts should have been accounted for"
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxBody.hs (L1311-1318)
```haskell
class ConwayEraTxBody era => DijkstraEraTxBody era where
  guardsTxBodyL :: Lens' (TxBody l era) (OSet (Credential Guard))

  subTransactionsTxBodyL :: Lens' (TxBody TopTx era) (OMap TxId (Tx SubTx era))

  requiredTopLevelGuardsL ::
    Lens' (TxBody SubTx era) (Map (Credential Guard) (StrictMaybe (Data era)))

```
