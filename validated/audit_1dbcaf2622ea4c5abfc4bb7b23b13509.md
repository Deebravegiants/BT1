### Title
`RequireGuard` Key-Hash Guard Credentials Require No Witness — Unauthorized Native-Script Satisfaction - (File: `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs`)

---

### Summary

In the Dijkstra era, the top-level transaction body carries a `guards` field (`OSet (Credential Guard)`). Native scripts can use the new `RequireGuard cred` primitive, which passes validation whenever `cred` is present in that set. For **script-hash** guard credentials the ledger correctly demands script execution; for **key-hash** guard credentials it demands nothing at all — no signature is required. Any transaction submitter can therefore insert an arbitrary `KeyHashObj kh` into the `guards` set without holding the corresponding private key, satisfying every `RequireGuard (KeyHashObj kh)` check in any native script that relies on it for authorization.

---

### Finding Description

**Step 1 — `getWitsVKeyNeeded` is not extended for guards.**

`DijkstraEra`'s `EraUTxO` instance delegates witness-key computation directly to Conway's implementation:

```haskell
-- eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs
getWitsVKeyNeeded _ = getConwayWitsVKeyNeeded
``` [1](#0-0) 

`getConwayWitsVKeyNeeded` (inherited from Shelley/Conway) collects witnesses for inputs, withdrawals, certificates, and pool owners. It has no knowledge of the Dijkstra `guards` field, so key-hash credentials placed there are never added to the required-witness set.

**Step 2 — Script-hash guards are correctly required; key-hash guards are silently skipped.**

`getDijkstraScriptsNeeded` adds script-hash guard credentials to `scriptsNeeded` via `guardingScriptsNeeded`:

```haskell
guardingScriptsNeeded = AlonzoScriptsNeeded $
  catMaybes $
    zipAsIxItem (txb ^. guardsTxBodyL) $
      \(AsIxItem idx cred) ->
        (\sh -> (GuardingPurpose (AsIxItem idx sh), sh)) <$> credScriptHash cred
``` [2](#0-1) 

`credScriptHash` returns `Nothing` for `KeyHashObj` credentials, so they are silently dropped. No corresponding path adds them to `witsVKeyNeeded`.

**Step 3 — `RequireGuard` checks only set membership.**

The Dijkstra native-script evaluator satisfies `RequireGuard` by a pure membership test:

```haskell
RequireGuard cred -> cred `OSet.member` guards
``` [3](#0-2) 

Because any submitter can freely populate the `guards` set with arbitrary key-hash credentials (no signature enforced), this check is trivially satisfiable by an adversary.

**Step 4 — The UTXOW guard-presence check does not enforce authorization.**

The only guard-related check in the top-level UTXOW rule verifies that sub-transaction-required guards are a subset of the top-level guards set:

```haskell
let requiredGuardsBySubTxs =
      foldMap (Map.keysSet . (^. bodyTxL . requiredTopLevelGuardsL)) subTxs
    topLevelGuards = OSet.toSet (txBody ^. guardsTxBodyL)
    missingGuards = requiredGuardsBySubTxs `Set.difference` topLevelGuards
runTestOnSignal $ failureOnNonEmptySet missingGuards MissingRequiredGuards
``` [4](#0-3) 

This is a set-containment check only. It does not verify that the top-level transaction is authorized by the guard credentials.

---

### Impact Explanation

A UTxO locked by a native script of the form `RequireGuard (KeyHashObj alice)` — or any compound script that relies on such a clause for authorization — can be spent by **any** transaction submitter who simply includes `KeyHashObj alice` in the top-level `guards` set, without possessing Alice's private key. This constitutes a direct, unauthorized loss of ADA or native assets through an invalid ledger state transition.

**Severity: Critical** — matches "Direct loss, creation, or destruction of ADA or native assets through an invalid ledger state transition."

---

### Likelihood Explanation

The `RequireGuard` primitive is a new Dijkstra-era feature explicitly designed to let scripts condition validation on the presence of a credential in the top-level guards. Script authors will naturally write `RequireGuard (KeyHashObj alice)` expecting it to require Alice's signature, by analogy with `RequireSignature`. The asymmetry between key-hash and script-hash guards is non-obvious and undocumented at the rule level. Any wallet or dApp that deploys a Dijkstra-era native script using `RequireGuard` with a key-hash credential is immediately vulnerable to fund theft by an unprivileged observer.

---

### Recommendation

Extend `getWitsVKeyNeeded` (or its Dijkstra override) to include key-hash credentials present in the top-level `guards` set, mirroring the treatment of key-hash credentials in withdrawals and certificates:

```haskell
getDijkstraWitsVKeyNeeded certState utxo txBody =
  getConwayWitsVKeyNeeded certState utxo txBody
    `Set.union` guardKeyHashes txBody

guardKeyHashes :: DijkstraEraTxBody era => TxBody l era -> Set (KeyHash Witness)
guardKeyHashes txBody =
  Set.fromList
    [ asWitness kh
    | KeyHashObj kh <- OSet.toList (txBody ^. guardsTxBodyL)
    ]
```

Then wire this into the `EraUTxO DijkstraEra` instance:

```haskell
getWitsVKeyNeeded _ = getDijkstraWitsVKeyNeeded
```

This ensures that including `KeyHashObj kh` in the `guards` set requires a valid signature from `kh`, restoring the authorization invariant that `RequireGuard (KeyHashObj kh)` implies `kh` signed the transaction.

---

### Proof of Concept

1. Alice creates a UTxO locked by the native script `RequireGuard (KeyHashObj alice_kh)`.
2. Attacker Bob constructs a top-level transaction that:
   - Spends Alice's UTxO (providing the native script as witness)
   - Sets `guards = OSet.singleton (KeyHashObj alice_kh)` in the top-level body
   - Provides **no** signature from `alice_kh`
3. The UTXOW rule calls `validateNeededWitnesses` using `getConwayWitsVKeyNeeded`, which does not include `alice_kh` → no missing-witness failure.
4. The native script evaluator calls `evalDijkstraNativeScript` with `guards = {KeyHashObj alice_kh}` → `RequireGuard (KeyHashObj alice_kh)` evaluates to `True`.
5. The transaction is accepted; Alice's funds are transferred to Bob without Alice's consent.

### Citations

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs (L139-139)
```haskell
  getWitsVKeyNeeded _ = getConwayWitsVKeyNeeded
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs (L173-176)
```haskell
    guardingScriptsNeeded = AlonzoScriptsNeeded $
      catMaybes $
        zipAsIxItem (txb ^. guardsTxBodyL) $
          \(AsIxItem idx cred) -> (\sh -> (GuardingPurpose (AsIxItem idx sh), sh)) <$> credScriptHash cred
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Scripts.hs (L575-575)
```haskell
      RequireGuard cred -> cred `OSet.member` guards
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
