Let me look at the GOV rule transition and the ratification rule to confirm the full impact chain.

### Title
Unelected Committee Members Can Bypass Mempool Vote Restriction via Direct Block Inclusion at Protocol Version ≤ 10 - (File: eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Mempool.hs)

---

### Summary

In the Conway era at protocol version ≤ 10, the check that disallows votes from unelected committee members exists only in the `MEMPOOL` rule, not in the `GOV` rule (block validation). A block producer can bypass the `MEMPOOL` check by including a vote transaction directly in a block. The block passes full ledger validation, the vote is stored in the ledger state, and after the committee member's election is enacted, their pre-vote is counted toward governance ratification — potentially enacting unauthorized treasury withdrawals, hard-fork initiations, or other governance actions.

---

### Finding Description

**Root cause — inconsistent check placement between two validation paths:**

In `Mempool.hs` (lines 123–135), the `unelectedCommitteeVoters` check is guarded by `unless (hardforkConwayDisallowUnelectedCommitteeFromVoting protVer)`. Because `hardforkConwayDisallowUnelectedCommitteeFromVoting pv = pvMajor pv > natVersion @10` returns `False` for protocol version 10, the `unless False` branch always executes, and the check **rejects** transactions containing votes from unelected committee members at the mempool level. [1](#0-0) 

In `Gov.hs` (lines 478–481), the same check is guarded by `when (hardforkConwayDisallowUnelectedCommitteeFromVoting ...)`. For protocol version 10, `when False` means the check is **never executed** during block validation. [2](#0-1) 

The hardfork flag definition confirms the asymmetry: [3](#0-2) 

**Result:** For protocol version 10, the `MEMPOOL` rule rejects the transaction, but the `GOV` rule (invoked during block body validation via `BBODY → LEDGERS → LEDGER → GOV`) accepts it. A block producer who includes the transaction directly in a block — bypassing the mempool — produces a valid block that all honest nodes accept.

The test in `LedgerSpec.hs` explicitly confirms this split: the transaction fails `submitFailingMempoolTx` but then succeeds via `withNoFixup $ submitTx_ txFixed` (direct ledger application, equivalent to block inclusion): [4](#0-3) 

**Vote counting after election:** The `committeeAcceptedRatio` function in `Ratify.hs` iterates over the map of elected cold keys, resolves each to its registered hot key via `csCommitteeCreds committeeState`, and then looks up that hot key in the `votes` map stored in `GovActionState`. Once the unelected member's election is enacted, their cold key enters `members`, their hot key resolves, and their pre-stored vote is counted. [5](#0-4) 

---

### Impact Explanation

The test `GovCertSpec.hs` (lines 210–228) provides a concrete end-to-end demonstration at protocol version 10:

1. An unelected committee member votes `VoteYes` on a treasury withdrawal governance action via direct ledger submission (bypassing mempool).
2. Immediately after, `isCommitteeAccepted gaiWithdrawal` returns `False` — the vote is not yet counted.
3. After one epoch, the member's election is enacted.
4. `isCommitteeAccepted gaiWithdrawal` returns `True` — the pre-vote is now counted.
5. After two more epochs, `expectMissingGovActionId gaiWithdrawal` confirms the treasury withdrawal was enacted. [6](#0-5) 

This constitutes **unauthorized enactment of a governance action** (treasury withdrawal, hard-fork initiation, protocol parameter change, or new constitution) because the vote was cast and counted before the member was legitimately elected, in direct violation of the rule the `MEMPOOL` check was designed to enforce. Impact: **Critical** — unauthorized governance/treasury action enacted.

---

### Likelihood Explanation

The attacker must simultaneously be (a) a proposed but not-yet-enacted committee member and (b) a block producer (stake pool operator). This is a realistic combination: a stake pool operator who is nominated to the Constitutional Committee can register their hot key, craft a vote transaction, and include it in a block they produce — all without any external cooperation. The leader schedule is public, so the attacker knows exactly when they will produce a block. No leaked keys, no supermajority, and no third-party compromise are required.

---

### Recommendation

Move the `unelectedCommitteeVoters` check from the `MEMPOOL` rule into the `GOV` rule unconditionally (for all protocol versions), not only when `hardforkConwayDisallowUnelectedCommitteeFromVoting` is active. The `MEMPOOL`-only placement for protocol version ≤ 10 creates a gap that any block producer can exploit. The check in `Gov.hs` should be:

```haskell
-- Remove the `when` guard; always enforce:
failOnNonEmpty
  (unelectedCommitteeVoters committee committeeState gsVotingProcedures)
  (injectFailure . UnelectedCommitteeVoters)
```

This mirrors the fix already applied for protocol version ≥ 11 and closes the bypass window for protocol version 10. [2](#0-1) 

---

### Proof of Concept

```
Setup (protocol version 10):
  1. Register a stake pool (attacker is a block producer).
  2. Propose adding attacker's cold key to the Constitutional Committee
     (UpdateCommittee action, not yet enacted).
  3. Register attacker's hot key via AuthCommitteeHotKeyTxCert.
  4. Submit a treasury withdrawal governance action (gaiWithdrawal).

Attack:
  5. Craft a VoteYes transaction from CommitteeVoter(attacker_hot_key) on gaiWithdrawal.
  6. Submit via mempool → rejected with ConwayMempoolFailure
     "Unelected committee members are not allowed to cast votes".
  7. Include the same transaction directly in a block the attacker produces
     → block passes full validation (GOV rule does not check unelected voters at PV 10).
  8. Vote is now stored in gasCommitteeVotes of gaiWithdrawal.

Outcome:
  9. Pass one epoch → attacker's UpdateCommittee election is enacted.
 10. isCommitteeAccepted gaiWithdrawal → True (pre-vote now counts).
 11. Pass two more epochs → treasury withdrawal is enacted; funds leave the treasury.
```

Confirmed by `GovCertSpec.hs` lines 210–228 and `LedgerSpec.hs` lines 313–318. [6](#0-5) [7](#0-6)

### Citations

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Mempool.hs (L123-135)
```haskell
    unless (hardforkConwayDisallowUnelectedCommitteeFromVoting protVer) $
      -- This check can completely be removed once mainnet switches to protocol
      -- version 11, since the same check has been implemented in the GOV rule.
      --
      -- Disallow votes by unelected committee members
      let addPrefix = ("Unelected committee members are not allowed to cast votes: " <>)
       in failOnNonEmpty
            ( unelectedCommitteeVoters
                (ledgerState ^. lsUTxOStateL . utxosGovStateL . committeeGovStateL)
                (ledgerState ^. lsCertStateL . certVStateL . vsCommitteeStateL)
                (tx ^. bodyTxL . votingProceduresTxBodyL)
            )
            (ConwayMempoolFailure . addPrefix . T.pack . show . NE.toList)
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Gov.hs (L478-481)
```haskell
  when (hardforkConwayDisallowUnelectedCommitteeFromVoting $ pp ^. ppProtocolVersionL) $
    failOnNonEmpty
      (unelectedCommitteeVoters committee committeeState gsVotingProcedures)
      (injectFailure . UnelectedCommitteeVoters)
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Era.hs (L259-262)
```haskell
-- | Starting with protocol version 11, we do not allow unelected committee
-- members to submit votes.
hardforkConwayDisallowUnelectedCommitteeFromVoting :: ProtVer -> Bool
hardforkConwayDisallowUnelectedCommitteeFromVoting pv = pvMajor pv > natVersion @10
```

**File:** eras/conway/impl/testlib/Test/Cardano/Ledger/Conway/Imp/LedgerSpec.hs (L281-318)
```haskell
    it "Unelected Committee voting" $ whenPostBootstrap $ do
      _ <- registerInitialCommittee
      ccCold <- KeyHashObj <$> freshKeyHash
      curEpochNo <- getsNES nesELL
      let action =
            UpdateCommittee
              SNothing
              mempty
              (Map.singleton ccCold (addEpochInterval curEpochNo (EpochInterval 7)))
              (1 %! 1)
      proposal <- mkProposal action
      submitTx_ $
        mkBasicTx (mkBasicTxBody & proposalProceduresTxBodyL .~ [proposal])
      ccHot <- registerCommitteeHotKey ccCold
      govActionId <- do
        accountAddress <- registerAccountAddress
        submitTreasuryWithdrawals [(accountAddress, Coin 1)]

      let
        tx =
          mkBasicTx $
            mkBasicTxBody
              & votingProceduresTxBodyL
                .~ VotingProcedures
                  ( Map.singleton
                      (CommitteeVoter ccHot)
                      (Map.singleton govActionId (VotingProcedure VoteYes SNothing))
                  )
      pv <- getProtVer
      if hardforkConwayDisallowUnelectedCommitteeFromVoting pv
        then
          submitFailingTx tx [injectFailure $ UnelectedCommitteeVoters [ccHot]]
        else do
          txFixed <-
            submitFailingMempoolTx "unallowed votes" tx $
              NonEmpty.singleton . injectFailure . ConwayMempoolFailure $
                "Unelected committee members are not allowed to cast votes: " <> T.pack (show (pure @[] ccHot))
          withNoFixup $ submitTx_ txFixed
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ratify.hs (L143-163)
```haskell
committeeAcceptedRatio members votes committeeState currentEpoch =
  yesVotes %? totalExcludingAbstain
  where
    accumVotes ::
      (Integer, Integer) ->
      Credential ColdCommitteeRole ->
      EpochNo ->
      (Integer, Integer)
    accumVotes (!yes, !tot) member expiry
      | currentEpoch > expiry = (yes, tot) -- member is expired, vote "abstain" (don't count it)
      | otherwise =
          case Map.lookup member (csCommitteeCreds committeeState) of
            Nothing -> (yes, tot) -- member is not registered, vote "abstain"
            Just (CommitteeMemberResigned _) -> (yes, tot) -- member has resigned, vote "abstain"
            Just (CommitteeHotCredential hotKey) ->
              case Map.lookup hotKey votes of
                Nothing -> (yes, tot + 1) -- member hasn't voted, vote "no"
                Just Abstain -> (yes, tot) -- member voted "abstain"
                Just VoteNo -> (yes, tot + 1) -- member voted "no"
                Just VoteYes -> (yes + 1, tot + 1) -- member voted "yes"
    (yesVotes, totalExcludingAbstain) = Map.foldlWithKey' accumVotes (0, 0) members
```

**File:** eras/conway/impl/testlib/Test/Cardano/Ledger/Conway/Imp/GovCertSpec.hs (L210-228)
```haskell
    it "at protocol version 10, the vote is counted once the committee update is enacted" $
      whenMajorVersion @10 $ do
        (drep, spo) <- setupGovEnv
        (gaiWithdrawal, initialMembers, proposedMember, gaiUpdateCommittee) <-
          proposeWithdrawalAndMember drep
        submitYesVote_ (DRepVoter drep) gaiUpdateCommittee
        submitYesVote_ (StakePoolVoter spo) gaiUpdateCommittee
        passEpoch
        expectMembers initialMembers
        proposedMemberHotKey <- registerCommitteeHotKey proposedMember
        submitYesVote_ (CommitteeVoter proposedMemberHotKey) gaiWithdrawal
        isCommitteeAccepted gaiWithdrawal `shouldReturn` False
        passEpoch
        expectMembers $ Set.singleton proposedMember
        ccShouldNotBeExpired proposedMember
        isCommitteeAccepted gaiWithdrawal `shouldReturn` True
        passNEpochs 2
        expectMissingGovActionId gaiUpdateCommittee
        expectMissingGovActionId gaiWithdrawal
```
