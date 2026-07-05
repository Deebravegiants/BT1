### Title
Unbounded Iteration Over All Registered DReps in `updateDormantDRepExpiry` Triggered by Any Governance Proposal Transaction - (File: eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Certs.hs)

### Summary
When a transaction containing at least one governance proposal is processed and the `numDormantEpochs` counter is non-zero, the Conway LEDGER/CERTS rule unconditionally iterates over the **entire** registered DRep map (`vsDReps`) to bump expiry values. This O(n-DReps) computation is performed inline during block validation, is not bounded by any protocol parameter, and is reachable by any unprivileged transaction author who submits a governance proposal.

### Finding Description

**Root cause — `updateDormantDRepExpiry`**

`updateDormantDRepExpiry` in `eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Certs.hs` (lines 308–328) performs a full `Map.map updateExpiry` over the entire `vsDReps` map whenever `numDormantEpochs ≠ 0`:

```haskell
updateDormantDRepExpiry currentEpoch vState =
  if numDormantEpochs == EpochNo 0
    then vState
    else
      vState
        & vsNumDormantEpochsL .~ EpochNo 0
        & vsDRepsL %~ Map.map updateExpiry   -- iterates ALL registered DReps
``` [1](#0-0) 

**Trigger path — `updateDormantDRepExpiries`**

`updateDormantDRepExpiries` (lines 257–267) calls the above function whenever the transaction body contains at least one governance proposal (`hasProposals`):

```haskell
updateDormantDRepExpiries tx currentEpoch =
  let hasProposals = not . OSet.null $ tx ^. bodyTxL . proposalProceduresTxBodyL
   in if hasProposals
        then certVStateL %~ updateDormantDRepExpiry currentEpoch
        else id
``` [2](#0-1) 

**Called inline during transaction validation**

In the Conway LEDGER rule (`eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ledger.hs`, lines 388–391), this is applied to every valid transaction before the UTXOW rule runs:

```haskell
pure $
  certState
    & updateDormantDRepExpiries tx curEpochNo
    & updateVotingDRepExpiries tx curEpochNo (pp ^. ppDRepActivityL)
    & certDStateL . accountsL %~ drainAccounts withdrawals
``` [3](#0-2) 

**No protocol-parameter bound on DRep count**

The `vsDReps` map grows with every `RegDRepTxCert` certificate. There is no protocol parameter capping the total number of registered DReps; the only friction is the per-DRep deposit (`ppDRepDepositL`). The `numDormantEpochs` counter is incremented at every epoch boundary where no governance proposals are active, so it naturally becomes non-zero during quiet governance periods.

### Impact Explanation

This is a **resource-limit bug**. Any unprivileged transaction author can submit a governance proposal transaction. If `numDormantEpochs > 0` at that moment (which occurs naturally after any epoch with no active proposals), the ledger performs an O(|vsDReps|) `Map.map` traversal inline during block validation. With a large DRep population this computation is unbounded by any protocol parameter, causing block validation to consume more CPU time than the ledger's design intends. Sustained or timed exploitation could cause honest block producers to exceed their slot window, degrading liveness. This matches the **Medium** allowed impact: *attacker-controlled transactions exceed intended validation limits*.

### Likelihood Explanation

The attack requires two preconditions:
1. **`numDormantEpochs > 0`** — occurs naturally after any epoch in which no governance proposals are submitted; the attacker does not need to cause this themselves.
2. **A large `vsDReps` map** — each DRep registration requires a deposit (`ppDRepDepositL`, currently 500 ADA on mainnet). Organically, the DRep population grows as governance participation increases; an adversary could also register many DReps at cost.

Because precondition (1) arises naturally and precondition (2) grows organically over time, the likelihood increases as the protocol matures and DRep participation grows. The attacker's entry point is simply submitting a valid governance proposal transaction — no privileged access is required.

### Recommendation

1. **Lazy / on-demand expiry**: Instead of eagerly updating all DRep expiries in a single `Map.map` pass, store the `numDormantEpochs` offset and compute each DRep's effective expiry lazily at query time (as is already done in `vsActualDRepExpiry`). This eliminates the O(n) traversal entirely.
2. **Protocol-parameter cap on DRep count**: Introduce a `ppMaxDReps` parameter to bound `|vsDReps|`, giving the O(n) cost a hard ceiling.
3. **Amortise across blocks**: If eager updates are required, spread the work across multiple blocks using a pulsing mechanism analogous to the existing `PulsingRewUpdate` / `DRepPulser` patterns already present in the codebase.

### Proof of Concept

1. Register N DReps on-chain (each paying `ppDRepDepositL`).
2. Allow one full epoch to pass with no governance proposals, causing `numDormantEpochs = 1`.
3. Submit a transaction containing a single `ProposalProcedure` (any valid governance action).
4. During LEDGER rule evaluation, `updateDormantDRepExpiries` detects `hasProposals = True` and calls `updateDormantDRepExpiry`, which executes `Map.map updateExpiry` over all N entries in `vsDReps`.
5. With N in the thousands (achievable organically as governance participation grows), this O(N) traversal occurs synchronously inside block validation for every such proposal transaction, with no protocol-level bound on N. [4](#0-3)

### Citations

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Certs.hs (L257-267)
```haskell
updateDormantDRepExpiries ::
  ( EraTx era
  , ConwayEraTxBody era
  , ConwayEraCertState era
  ) =>
  Tx l era -> EpochNo -> CertState era -> CertState era
updateDormantDRepExpiries tx currentEpoch =
  let hasProposals = not . OSet.null $ tx ^. bodyTxL . proposalProceduresTxBodyL
   in if hasProposals
        then certVStateL %~ updateDormantDRepExpiry currentEpoch
        else id
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Certs.hs (L308-328)
```haskell
updateDormantDRepExpiry ::
  -- | Current Epoch
  EpochNo ->
  VState era ->
  VState era
updateDormantDRepExpiry currentEpoch vState =
  if numDormantEpochs == EpochNo 0
    then vState
    else
      vState
        & vsNumDormantEpochsL .~ EpochNo 0
        & vsDRepsL %~ Map.map updateExpiry
  where
    numDormantEpochs = vState ^. vsNumDormantEpochsL
    updateExpiry =
      drepExpiryL
        %~ \currentExpiry ->
          let actualExpiry = binOpEpochNo (+) numDormantEpochs currentExpiry
           in if actualExpiry < currentEpoch
                then currentExpiry
                else actualExpiry
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ledger.hs (L388-391)
```haskell
                  certState
                    & updateDormantDRepExpiries tx curEpochNo
                    & updateVotingDRepExpiries tx curEpochNo (pp ^. ppDRepActivityL)
                    & certDStateL . accountsL %~ drainAccounts withdrawals
```
