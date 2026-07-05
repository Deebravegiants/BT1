### Title
Unprivileged Direct Deposit Permanently Blocks Stake Key Deregistration via Non-Zero Balance Guard — (File: `eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Deleg.hs`)

---

### Summary

In the Dijkstra era, any unprivileged transaction sender can include a `directDepositsTxBodyL` field targeting any registered stake account. Because the `ConwayUnRegCert` handler (reused by Dijkstra via `Conway.CERTS`) blocks deregistration whenever the account balance is non-zero, an attacker can front-run a victim's deregistration transaction with a tiny direct deposit, leaving a residual balance that causes the deregistration to fail. The attacker can repeat this indefinitely at low cost, permanently preventing the victim from recovering their stake key deposit.

---

### Finding Description

**Root cause 1 — zero-balance guard on deregistration.**

`eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Deleg.hs` lines 260–268 implement `checkStakeKeyHasZeroRewardBalance` inside the `ConwayUnRegCert` branch:

```haskell
checkStakeKeyHasZeroRewardBalance = do
  accountState <- mAccountState
  let balanceCompact = accountState ^. balanceAccountStateL
  guard (balanceCompact /= mempty)
  Just $ fromCompact balanceCompact
failOnJust
  checkStakeKeyHasZeroRewardBalance
  (injectFailure . StakeKeyHasNonZeroAccountBalanceDELEG)
```

If the account balance is anything other than zero the certificate is rejected. The identical guard exists in `eras/shelley/impl/src/Cardano/Ledger/Shelley/Rules/Deleg.hs` lines 272–277 (`StakeKeyNonZeroAccountBalanceDELEG`). [1](#0-0) 

**Root cause 2 — unprivileged direct deposits to arbitrary accounts.**

The Dijkstra era introduces `dtbrDirectDeposits :: !DirectDeposits` in the top-level transaction body (`eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxBody.hs` line 185). [2](#0-1) 

`DirectDeposits` is simply `newtype DirectDeposits = DirectDeposits {unDirectDeposits :: Map AccountAddress Coin}` — a map from any account address to a coin amount, with no authorization requirement. [3](#0-2) 

`applyDirectDeposits` in `libs/cardano-ledger-core/src/Cardano/Ledger/State/Account.hs` unconditionally adds each amount to the matching account's `balanceAccountStateL`: [4](#0-3) 

```haskell
applyDirectDeposits (DirectDeposits dd) =
  updateAccountBalances
    (\amount account -> addCompactCoin amount (account ^. balanceAccountStateL))
    dd
```

**Root cause 3 — ordering in the ENTITIES rule.**

`eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Entities.hs` lines 203–216 show the execution order: withdrawals are applied first, then certificates (including `ConwayUnRegCert`) are processed, and only then are direct deposits applied: [5](#0-4) 

```haskell
let certStateBeforeCerts =
      certState
        & certDStateL . accountsL %~ applyWithdrawals withdrawals
certStateAfterCerts <-
  trans @(EraRule "CERTS" era) $ TRC (certsEnv, certStateBeforeCerts, certificates)

let directDeposits = tx ^. bodyTxL . directDepositsTxBodyL
    accountsAfterCerts = certStateAfterCerts ^. certDStateL . accountsL
failOnJust (directDepositsMissingAccounts directDeposits accountsAfterCerts) $
  injectFailure . DirectDepositsToMissingAccounts

pure $ certStateAfterCerts & certDStateL . accountsL %~ applyDirectDeposits directDeposits
```

This ordering means a direct deposit from a *different* transaction (submitted in the same block, ordered before the victim's transaction) can raise the victim's balance before the victim's `ConwayUnRegCert` is evaluated.

**The interaction.**

In non-legacy Dijkstra mode, `validateWithdrawals` uses `withdrawalsThatExceedAccountBalance` — withdrawals only need to be ≤ the balance, not equal to it. [6](#0-5)  This means if the victim constructs a transaction withdrawing exactly their known balance X and then deregistering, but the attacker front-runs with a direct deposit of Y lovelace, the victim's withdrawal of X succeeds (X ≤ X+Y) but leaves Y lovelace in the account, causing the deregistration to fail with `StakeKeyHasNonZeroAccountBalanceDELEG`.

---

### Impact Explanation

The victim's stake key deposit (2 ADA on mainnet) is frozen for as long as the attacker sustains the front-running. The victim cannot atomically drain an unknown balance and deregister in a single transaction because the balance is attacker-controlled between transaction construction and block inclusion. This matches the **Medium** allowed impact: *attacker-controlled transactions modify deposits, refunds, or withdrawals outside design parameters*.

---

### Likelihood Explanation

The attack requires only a standard Dijkstra transaction with a `directDepositsTxBodyL` entry targeting the victim's account address. No privileged role, key leak, or governance majority is needed. The attacker's per-block cost is one transaction fee (~0.17 ADA) plus 1 lovelace. A targeted victim with a 2 ADA deposit can be griefed indefinitely at negligible cost. The attack is reachable from any unprivileged transaction sender.

---

### Recommendation

1. **Remove the zero-balance guard from `ConwayUnRegCert`** (and `UnRegTxCert`). The deposit refund is tracked independently in `depositAccountStateL`; the reward balance can be returned to the owner as part of the deregistration output, as the spec already describes. This mirrors the recommendation in the original report: the check is no longer necessary once the relevant value is stored separately.

2. Alternatively, **require authorization to send direct deposits to an account** — e.g., require a witness from the account's staking credential before a third party can increase its balance.

---

### Proof of Concept

1. Alice registers stake key `K`, earns rewards, withdraws them (balance = 0).
2. Alice constructs `TxA`: withdrawal of 0 lovelace + `ConwayUnRegCert K`.
3. Bob submits `TxB` (ordered before `TxA` in the same block): `directDepositsTxBodyL = {Alice's account → 1 lovelace}`.
4. After `TxB`: Alice's balance = 1 lovelace.
5. `TxA` is evaluated: `checkStakeKeyHasZeroRewardBalance` fires → `StakeKeyHasNonZeroAccountBalanceDELEG 1` → `TxA` rejected.
6. Alice's 2 ADA deposit remains locked. Bob repeats step 3 every block.

Relevant code path:
- `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Entities.hs:207` — `applyWithdrawals` (Alice's 0-withdrawal applied)
- `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Entities.hs:208–209` — `Conway.CERTS` processes `ConwayUnRegCert K` → fails at `checkStakeKeyHasZeroRewardBalance` (balance = 1 ≠ 0)
- `eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Deleg.hs:260–268` — the blocking guard
- `libs/cardano-ledger-core/src/Cardano/Ledger/State/Account.hs:290–298` — `applyDirectDeposits` (Bob's deposit applied in `TxB`) [1](#0-0) [7](#0-6) [4](#0-3) [3](#0-2) [2](#0-1)

### Citations

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Deleg.hs (L260-268)
```haskell
          checkStakeKeyHasZeroRewardBalance = do
            accountState <- mAccountState
            let balanceCompact = accountState ^. balanceAccountStateL
            guard (balanceCompact /= mempty)
            Just $ fromCompact balanceCompact
      failOnJust checkInvalidRefund id
      failOnJust
        checkStakeKeyHasZeroRewardBalance
        (injectFailure . StakeKeyHasNonZeroAccountBalanceDELEG)
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxBody.hs (L185-186)
```haskell
    , dtbrDirectDeposits :: !DirectDeposits
    , dtbrAccountBalanceIntervals :: !(AccountBalanceIntervals era)
```

**File:** libs/cardano-ledger-core/src/Cardano/Ledger/Address.hs (L991-993)
```haskell
newtype DirectDeposits = DirectDeposits {unDirectDeposits :: Map AccountAddress Coin}
  deriving (Show, Eq, Generic)
  deriving newtype (NoThunks, NFData, EncCBOR, DecCBOR)
```

**File:** libs/cardano-ledger-core/src/Cardano/Ledger/State/Account.hs (L290-298)
```haskell
applyDirectDeposits ::
  EraAccounts era =>
  DirectDeposits ->
  Accounts era ->
  Accounts era
applyDirectDeposits (DirectDeposits dd) =
  updateAccountBalances
    (\amount account -> addCompactCoin amount (account ^. balanceAccountStateL))
    dd
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Entities.hs (L203-216)
```haskell
  let certStateBeforeCerts =
        certState
          & Conway.updateDormantDRepExpiries tx curEpoch
          & Conway.updateVotingDRepExpiries tx curEpoch (pp ^. ppDRepActivityL)
          & certDStateL . accountsL %~ applyWithdrawals withdrawals
  certStateAfterCerts <-
    trans @(EraRule "CERTS" era) $ TRC (certsEnv, certStateBeforeCerts, certificates)

  let directDeposits = tx ^. bodyTxL . directDepositsTxBodyL
      accountsAfterCerts = certStateAfterCerts ^. certDStateL . accountsL
  failOnJust (directDepositsMissingAccounts directDeposits accountsAfterCerts) $
    injectFailure . DirectDepositsToMissingAccounts

  pure $ certStateAfterCerts & certDStateL . accountsL %~ applyDirectDeposits directDeposits
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Entities.hs (L235-241)
```haskell
      else do
        let (missingWithdrawals, exceededWithdrawals) =
              case withdrawalsThatExceedAccountBalance withdrawals network accounts of
                Nothing -> (Map.empty, Map.empty)
                Just (missing, exceeded) -> (unWithdrawals missing, exceeded)
        failOnNonEmptyMap exceededWithdrawals WithdrawalAmountsExceedAccountBalances
        pure missingWithdrawals
```
