### Title
Missing DRep Delegation Check for Script-Hash Staking Credentials in Withdrawal Validation — (`File: eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ledger.hs`)

---

### Summary

The `validateWithdrawalsDelegated` function in the Conway (and Dijkstra) `LEDGER` rule silently skips DRep-delegation enforcement for script-hash staking credentials. Only key-hash credentials are extracted and checked; `ScriptHashObj` credentials pass the check unconditionally. This is the direct analog of the external report's missing token-address validation: a user-supplied value (the staking credential type) is never validated against the required set (DRep-delegated credentials), allowing withdrawals outside design parameters.

---

### Finding Description

`validateWithdrawalsDelegated` is responsible for enforcing the Conway governance rule that every staking credential used in a reward withdrawal must be delegated to a DRep:

```haskell
validateWithdrawalsDelegated accounts tx =
  let wdrls = unWithdrawals $ tx ^. bodyTxL . withdrawalsTxBodyL
      wdrlsKeyHashes =
        [ kh | (ra, _) <- Map.toList wdrls
             , Just kh <- [credKeyHash $ ra ^. accountAddressCredentialL]
        ]
      isNotDRepDelegated keyHash = isNothing $ do
        accountState <- lookupAccountState (KeyHashObj keyHash) accounts
        accountState ^. dRepDelegationAccountStateL
      nonExistentDelegations = filter isNotDRepDelegated wdrlsKeyHashes
   in failureOnNonEmpty nonExistentDelegations ConwayWdrlNotDelegatedToDRep
``` [1](#0-0) 

The list comprehension uses `credKeyHash`, which is defined as:

```haskell
credKeyHash :: Credential r -> Maybe (KeyHash r)
credKeyHash = \case
  KeyHashObj hk -> Just hk
  ScriptHashObj _ -> Nothing   -- silently returns Nothing
``` [2](#0-1) 

Because `credKeyHash` returns `Nothing` for `ScriptHashObj`, every script-hash staking credential is silently dropped from `wdrlsKeyHashes`. The DRep-delegation predicate is never evaluated for those credentials, so the rule always passes for them.

Script-hash staking credentials are fully supported in Conway: `ConwayDelegCert cred (DelegVote drep)` accepts any `Credential Staking`, including `ScriptHashObj`. [3](#0-2) 

The same `Conway.validateWithdrawalsDelegated` is re-used verbatim in the Dijkstra `ENTITIES` and `SUBENTITIES` rules: [4](#0-3) [5](#0-4) 

---

### Impact Explanation

The Conway governance design requires that any staking credential withdrawing rewards must be delegated to a DRep. This is the mechanism by which the protocol incentivises governance participation. A user who controls a script-based staking credential (e.g., a Plutus or native-script stake key) can accumulate rewards and withdraw them in a transaction that carries no DRep delegation, bypassing the intended validation limit. The withdrawal modifies the reward balance outside design parameters — the exact Medium-impact category: *"Attacker-controlled transactions… modify… withdrawals outside design parameters."*

---

### Likelihood Explanation

Script-hash staking credentials are a first-class feature of the Cardano address model and are used in practice (e.g., multi-sig or Plutus-controlled stake). Any holder of such a credential who has accumulated rewards can exploit this silently — no special privilege, no governance majority, no leaked key is required. The attacker simply submits a standard withdrawal transaction. The entry path is fully unprivileged.

---

### Recommendation

Replace the key-hash-only extraction with a check over all credential types. For key-hash credentials, verify DRep delegation as today. For script-hash credentials, verify that the corresponding account state carries a DRep delegation (using `lookupAccountState (ScriptHashObj sh) accounts >>= (^. dRepDelegationAccountStateL)`). The fix should be applied symmetrically in `validateWithdrawalsDelegated` and propagated to the Dijkstra `ENTITIES` / `SUBENTITIES` rules that call it.

---

### Proof of Concept

1. Register a script-hash staking credential (e.g., a native-script or Plutus script hash) via `RegDepositTxCert (ScriptHashObj sh) deposit`.
2. Accumulate rewards to that credential (e.g., via pool delegation and epoch advancement).
3. Submit a withdrawal transaction referencing `AccountAddress Testnet (AccountId (ScriptHashObj sh))` with the full reward balance, **without** ever submitting a `DelegTxCert (ScriptHashObj sh) (DelegVote drep)` certificate.
4. Observe that the transaction is accepted: `validateWithdrawalsDelegated` extracts `credKeyHash (ScriptHashObj sh) = Nothing`, so `wdrlsKeyHashes` is empty, `nonExistentDelegations` is empty, and `ConwayWdrlNotDelegatedToDRep` is never raised.
5. The reward balance is drained to the transaction outputs without any DRep delegation having been established, violating the Conway governance participation invariant.

### Citations

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ledger.hs (L473-488)
```haskell
validateWithdrawalsDelegated ::
  ( EraTx era
  , ConwayEraCertState era
  ) =>
  Accounts era -> Tx l era -> Test (ConwayLedgerPredFailure era)
validateWithdrawalsDelegated accounts tx =
  let wdrls = unWithdrawals $ tx ^. bodyTxL . withdrawalsTxBodyL
      wdrlsKeyHashes =
        [ kh | (ra, _) <- Map.toList wdrls, Just kh <- [credKeyHash $ ra ^. accountAddressCredentialL]
        ]
      isNotDRepDelegated keyHash = isNothing $ do
        accountState <- lookupAccountState (KeyHashObj keyHash) accounts
        accountState ^. dRepDelegationAccountStateL
      nonExistentDelegations =
        filter isNotDRepDelegated wdrlsKeyHashes
   in failureOnNonEmpty nonExistentDelegations ConwayWdrlNotDelegatedToDRep
```

**File:** libs/cardano-ledger-core/src/Cardano/Ledger/Credential.hs (L204-207)
```haskell
credKeyHash :: Credential r -> Maybe (KeyHash r)
credKeyHash = \case
  KeyHashObj hk -> Just hk
  ScriptHashObj _ -> Nothing
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/TxCert.hs (L481-487)
```haskell
  | -- | Delegate staking credentials to a delegatee. Staking credential must already be registered.
    ConwayDelegCert !(Credential Staking) !Delegatee
  | -- | This is a new type of certificate, which allows to register staking credential
    -- and delegate within a single certificate. Deposit is required and must match the
    -- expected deposit amount specified by `ppKeyDepositL` in the protocol parameters.
    ConwayRegDelegCert !(Credential Staking) !Delegatee !Coin
  deriving (Show, Generic, Eq, Ord)
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Entities.hs (L197-197)
```haskell
  runTest $ Conway.validateWithdrawalsDelegated accounts tx
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubEntities.hs (L163-163)
```haskell
  runTest $ Conway.validateWithdrawalsDelegated accounts tx
```
