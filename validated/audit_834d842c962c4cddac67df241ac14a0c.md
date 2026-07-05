### Title
Script-Based Staking Credentials Bypass DRep Delegation Enforcement in `validateWithdrawalsDelegated` — (File: `eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ledger.hs`)

---

### Summary

The Conway LEDGER rule's `validateWithdrawalsDelegated` function enforces that staking credentials performing withdrawals must be delegated to a DRep. However, the function silently skips all `ScriptHashObj` staking credentials by using `credKeyHash`, which returns `Nothing` for script credentials. As a result, any script-based staking credential can withdraw accumulated rewards without ever being delegated to a DRep, bypassing the Conway governance participation requirement that applies to all staking credentials.

---

### Finding Description

In `eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ledger.hs`, the function `validateWithdrawalsDelegated` is invoked (post-bootstrap, protocol version ≥ 10) to ensure that every withdrawal in a transaction comes from a staking credential that is delegated to a DRep:

```haskell
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
``` [1](#0-0) 

The list comprehension on line 481 uses `credKeyHash`:

```haskell
[ kh | (ra, _) <- Map.toList wdrls, Just kh <- [credKeyHash $ ra ^. accountAddressCredentialL] ]
```

`credKeyHash` is defined as:

```haskell
credKeyHash :: Credential r -> Maybe (KeyHash r)
credKeyHash = \case
  KeyHashObj hk -> Just hk
  ScriptHashObj _ -> Nothing
``` [2](#0-1) 

Because `credKeyHash` returns `Nothing` for every `ScriptHashObj`, the list comprehension silently drops all script-hash staking credentials from `wdrlsKeyHashes`. The subsequent `isNotDRepDelegated` check and `ConwayWdrlNotDelegatedToDRep` failure are therefore **never applied to script credentials**. A transaction withdrawing rewards from a `ScriptHashObj` staking account that has no DRep delegation at all passes `validateWithdrawalsDelegated` without error.

The call site confirms the check is active post-bootstrap:

```haskell
unless (hardforkConwayBootstrapPhase (pp ^. ppProtocolVersionL)) $ do
  runTest $ validateWithdrawalsDelegated accounts tx
``` [3](#0-2) 

The inline comment at the call site further confirms the scope is intentionally (or mistakenly) limited to key hashes:

```
-- Starting with version 10, we don't allow withdrawals into RewardAcounts that are
-- KeyHashes and not delegated to Dreps.
``` [4](#0-3) 

The `Credential` type has exactly two constructors — `KeyHashObj` and `ScriptHashObj` — and the check covers only one of them: [5](#0-4) 

The existing test titled `"Withdraw from delegated and non-delegated staking script"` only exercises the delegated path (it delegates to `DRepAlwaysAbstain` before withdrawing); it does not assert that a non-delegated script credential is rejected, leaving the bypass untested: [6](#0-5) 

---

### Impact Explanation

Conway's governance design (CIP-1694) requires every staking credential that performs a reward withdrawal to be delegated to a DRep, so that all ADA holders participate in on-chain governance. By silently omitting `ScriptHashObj` credentials from the delegation check, the ledger allows script-controlled staking accounts to drain their reward balances without any DRep delegation, withdrawing ADA outside the intended governance-participation constraint. This is a **withdrawal outside design parameters** — matching the Medium impact tier: *"Attacker-controlled transactions … modify … withdrawals outside design parameters."*

---

### Likelihood Explanation

Script-based staking credentials (`ScriptHashObj`) are a first-class, fully supported credential type since Shelley. Any transaction author can register a staking script, accumulate rewards (e.g., via stake pool delegation), and submit a withdrawal transaction without ever issuing a DRep delegation certificate. No privileged access, governance majority, or key compromise is required. The bypass is unconditional for all protocol versions ≥ 10 (post-bootstrap Conway).

---

### Recommendation

Replace the `credKeyHash`-based filter with a check that covers **both** credential types. For `KeyHashObj` credentials, verify DRep delegation as today. For `ScriptHashObj` credentials, apply an equivalent check — either requiring a DRep delegation entry in the accounts map, or explicitly documenting and enforcing the intended policy for script credentials. The predicate failure `ConwayWdrlNotDelegatedToDRep` currently only carries a list of `KeyHash Staking`; it should be extended to also report script credentials that fail the check.

---

### Proof of Concept

1. Register a staking script credential `ScriptHashObj sh` (no DRep delegation certificate issued).
2. Delegate to a stake pool to earn rewards.
3. After rewards accumulate, submit a transaction with a withdrawal from the script's account address.
4. `validateWithdrawalsDelegated` builds `wdrlsKeyHashes` via `credKeyHash`; `credKeyHash (ScriptHashObj sh)` returns `Nothing`, so the credential is excluded from the list.
5. `nonExistentDelegations` is empty; `failureOnNonEmpty` does not fire.
6. The transaction is accepted and rewards are withdrawn — despite the staking credential having no DRep delegation, in violation of the Conway governance participation rule.

### Citations

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ledger.hs (L373-374)
```haskell
          -- Starting with version 10, we don't allow withdrawals into RewardAcounts that are
          -- KeyHashes and not delegated to Dreps.
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ledger.hs (L379-380)
```haskell
          unless (hardforkConwayBootstrapPhase (pp ^. ppProtocolVersionL)) $ do
            runTest $ validateWithdrawalsDelegated accounts tx
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ledger.hs (L478-488)
```haskell
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

**File:** libs/cardano-ledger-core/src/Cardano/Ledger/Credential.hs (L98-101)
```haskell
data Credential (kr :: KeyRole)
  = ScriptHashObj !ScriptHash
  | KeyHashObj !(KeyHash kr)
  deriving (Show, Eq, Generic, Ord)
```

**File:** libs/cardano-ledger-core/src/Cardano/Ledger/Credential.hs (L204-207)
```haskell
credKeyHash :: Credential r -> Maybe (KeyHash r)
credKeyHash = \case
  KeyHashObj hk -> Just hk
  ScriptHashObj _ -> Nothing
```

**File:** eras/conway/impl/testlib/Test/Cardano/Ledger/Conway/Imp/LedgerSpec.hs (L200-215)
```haskell
  it "Withdraw from delegated and non-delegated staking script" $ do
    modifyPParams $ ppGovActionLifetimeL .~ EpochInterval 2
    let scriptHash = hashPlutusScript $ alwaysSucceedsNoDatum SPlutusV3
    let cred = ScriptHashObj scriptHash
    ra <- registerStakeCredential cred
    void $ delegateToDRep cred (Coin 1_000_000) DRepAlwaysAbstain
    submitAndExpireProposalToMakeReward cred
    balance <- getBalance cred

    submitTx_ $
      mkBasicTx $
        mkBasicTxBody & withdrawalsTxBodyL .~ Withdrawals [(ra, balance)]

    submitTx_ $
      mkBasicTx $
        mkBasicTxBody & withdrawalsTxBodyL .~ Withdrawals [(ra, mempty)]
```
