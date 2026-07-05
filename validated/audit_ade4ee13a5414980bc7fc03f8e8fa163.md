### Title
Unelected Committee Members Can Cast Governance Votes via Block-Producer Bypass at Protocol Version 10 — (File: `eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Gov.hs`)

---

### Summary

At Conway protocol version 10, the `GOV` ledger rule does not enforce the restriction against unelected committee members casting votes. The only guard is placed in the `MEMPOOL` rule, which is not applied during block validation. A block producer can therefore include a transaction containing a vote from a proposed-but-not-yet-enacted committee member directly in a block, bypassing the mempool check. Once the corresponding `UpdateCommittee` action is enacted at the epoch boundary, the pre-cast vote is counted toward ratification, potentially enacting an unauthorized governance action.

---

### Finding Description

**Root cause — missing check in the GOV rule at protocol version 10**

In `eras/conway/impl/src/Cardano/Ledger/Conway/Era.hs`, the hardfork flag that enables the unelected-committee-voter check is defined as:

```haskell
-- | Starting with protocol version 11, we do not allow unelected committee
-- members to submit votes.
hardforkConwayDisallowUnelectedCommitteeFromVoting :: ProtVer -> Bool
hardforkConwayDisallowUnelectedCommitteeFromVoting pv = pvMajor pv > natVersion @10
``` [1](#0-0) 

The GOV transition rule (`conwayGovTransition`) gates the unelected-voter rejection behind this flag:

```haskell
when (hardforkConwayDisallowUnelectedCommitteeFromVoting $ pp ^. ppProtocolVersionL) $
    failOnNonEmpty
      (unelectedCommitteeVoters committee committeeState gsVotingProcedures)
      (injectFailure . UnelectedCommitteeVoters)
``` [2](#0-1) 

Because `pvMajor pv > natVersion @10` is `False` at protocol version 10, the `when` branch is never entered, and the GOV rule accepts votes from unelected committee members without error.

**The MEMPOOL rule is the only guard — and it is not applied during block validation**

The MEMPOOL rule does apply the check at protocol version 10:

```haskell
unless (hardforkConwayDisallowUnelectedCommitteeFromVoting protVer) $
  -- This check can completely be removed once mainnet switches to protocol
  -- version 11, since the same check has been implemented in the GOV rule.
  --
  -- Disallow votes by unelected committee members
  ...
  failOnNonEmpty
    ( unelectedCommitteeVoters ... )
    (ConwayMempoolFailure . addPrefix . T.pack . show . NE.toList)
``` [3](#0-2) 

The comment explicitly acknowledges that the MEMPOOL check is a temporary stand-in until the GOV rule check is activated at protocol version 11. However, the MEMPOOL rule is only invoked when a transaction enters the mempool — it is **not** part of the LEDGER/GOV validation path applied when a block is validated. A block producer can construct and include a transaction directly in a block, skipping the MEMPOOL rule entirely.

**Vote storage and deferred counting**

`GovActionState` stores committee votes in a plain map keyed by `Credential HotCommitteeRole`:

```haskell
gasCommitteeVotes :: Map (Credential HotCommitteeRole) Vote
``` [4](#0-3) 

The ratification rule uses `authorizedElectedHotCommitteeCredentials` to filter which stored votes count. Once the `UpdateCommittee` action is enacted at the epoch boundary, the previously unelected member's hot credential enters the elected set, and the pre-cast vote is retroactively counted toward ratification.

The test suite confirms this behavior explicitly at protocol version 10:

```haskell
submitYesVote_ (CommitteeVoter proposedMemberHotKey) gaiWithdrawal
isCommitteeAccepted gaiWithdrawal `shouldReturn` False
passEpoch
expectMembers $ Set.singleton proposedMember
isCommitteeAccepted gaiWithdrawal `shouldReturn` True
``` [5](#0-4) 

The test also confirms that bypassing the mempool (`withNoFixup $ submitTx_`) allows the vote to reach the ledger at protocol version 10 even though the mempool rejects it: [6](#0-5) 

**Attacker-controlled entry path**

1. Attacker (or colluding party) is a registered DRep and stake pool operator.
2. Attacker submits an `UpdateCommittee` proposal adding their cold credential; it is ratified by DReps and SPOs.
3. Attacker registers a hot key for their cold credential (`AuthCommitteeHotKeyTxCert`).
4. Before the epoch boundary (enactment), the attacker, acting as a block producer, constructs a transaction containing a `CommitteeVoter` vote on a target governance action (e.g., a `TreasuryWithdrawals` or `HardForkInitiation`) and includes it directly in a block they produce — bypassing the MEMPOOL check.
5. The GOV rule at protocol version 10 accepts the transaction (no `UnelectedCommitteeVoters` check).
6. At the epoch boundary, the `UpdateCommittee` action is enacted; the attacker's hot credential enters the elected set.
7. The pre-cast vote is now counted toward ratification of the target governance action.

---

### Impact Explanation

**Critical — Unauthorized governance action enacted.**

If the target governance action (e.g., `TreasuryWithdrawals`, `HardForkInitiation`, `NewConstitution`, `ParameterChange`) is near the committee acceptance threshold, the attacker's pre-cast vote can tip ratification. This allows an unauthorized governance action to be enacted — including direct ADA treasury withdrawals, unauthorized hard-fork initiations, or protocol-parameter changes — without the committee threshold having been legitimately met at the time of voting.

---

### Likelihood Explanation

**Medium.** The attacker must control a stake pool (block producer) and either be the proposed committee member or collude with them. Both roles are permissionless on Cardano. The timing window (between ratification of the `UpdateCommittee` action and its enactment at the epoch boundary) is one full epoch (~5 days), providing ample opportunity. The attack is deterministic and requires no cryptographic break.

---

### Recommendation

The `hardforkConwayDisallowUnelectedCommitteeFromVoting` guard in `conwayGovTransition` should be removed and the `unelectedCommitteeVoters` check should be applied unconditionally, regardless of protocol version. The MEMPOOL-only defense is insufficient because block producers can bypass the mempool. The fix already exists for protocol version ≥ 11; the same check should be backported to protocol version 10 in the GOV rule. [2](#0-1) 

---

### Proof of Concept

The existing test suite provides a deterministic PoC. In `Test.Cardano.Ledger.Conway.Imp.LedgerSpec`, the test `"Unelected Committee voting"` at protocol version 10 demonstrates:

1. A proposed (unelected) committee member registers a hot key.
2. A vote transaction is submitted via `withNoFixup $ submitTx_` (bypassing the mempool).
3. The GOV rule accepts the transaction — no `UnelectedCommitteeVoters` failure is raised. [7](#0-6) 

The companion test in `GovCertSpec` confirms that once the `UpdateCommittee` action is enacted, `isCommitteeAccepted` flips from `False` to `True` — the pre-cast vote is retroactively counted: [8](#0-7)

### Citations

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Era.hs (L259-262)
```haskell
-- | Starting with protocol version 11, we do not allow unelected committee
-- members to submit votes.
hardforkConwayDisallowUnelectedCommitteeFromVoting :: ProtVer -> Bool
hardforkConwayDisallowUnelectedCommitteeFromVoting pv = pvMajor pv > natVersion @10
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Gov.hs (L478-481)
```haskell
  when (hardforkConwayDisallowUnelectedCommitteeFromVoting $ pp ^. ppProtocolVersionL) $
    failOnNonEmpty
      (unelectedCommitteeVoters committee committeeState gsVotingProcedures)
      (injectFailure . UnelectedCommitteeVoters)
```

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

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Governance/Procedures.hs (L301-318)
```haskell
      , Interns (Credential HotCommitteeRole)
      )
  decSharePlusCBOR =
    decodeRecordNamedT "GovActionState" (const 7) $ do
      gasId <- lift decCBOR

      (cs, ks, cd, ch) <- get
      gasCommitteeVotes <- lift $ decShareCBOR (ch, mempty)
      gasDRepVotes <- lift $ decShareCBOR (cd, mempty)
      gasStakePoolVotes <- lift $ decShareCBOR (ks, mempty)

      -- DRep votes do not contain any new credentials, thus only additon of interns for SPOs and CCs
      put (cs, ks <> internsFromMap gasStakePoolVotes, cd, ch <> internsFromMap gasCommitteeVotes)

      gasProposalProcedure <- lift decCBOR
      gasProposedIn <- lift decCBOR
      gasExpiresAfter <- lift decCBOR
      pure GovActionState {..}
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
