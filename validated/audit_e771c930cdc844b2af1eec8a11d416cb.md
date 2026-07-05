### Title
`directDeposits` Omitted from Value Conservation Check Enables ADA Creation — (File: `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs`)

---

### Summary

The Dijkstra era introduces a `directDeposits` field in the transaction body that allows a transaction to credit ADA directly into registered account balances. However, neither the `consumed` nor the `produced` side of the ledger's value-conservation equation (`consumed pp utxo txb = produced pp certState txb`) accounts for `directDeposits`. Because `applyDirectDeposits` unconditionally adds those amounts to account balances after the UTxO check passes, an unprivileged transaction author can include the same ADA in both UTxO outputs and `directDeposits`, causing the ledger to accept a net increase in the total ADA supply.

---

### Finding Description

**New field — `DirectDeposits`**

`DirectDeposits` is a `Map AccountAddress Coin` carried in the Dijkstra-era transaction body for both top-level and sub-transactions. [1](#0-0) 

**How `directDeposits` are applied — `applyDirectDeposits`**

In `dijkstraEntitiesTransition` (the `ENTITIES` rule), after certificates are processed, `applyDirectDeposits` is called unconditionally to add each entry's `Coin` amount to the matching account's `balanceAccountStateL`: [2](#0-1) 

The only guard is that target accounts must be registered: [3](#0-2) 

There is no check that the ADA being deposited was deducted from anywhere.

**Value-conservation check — `validateValueNotConservedUT

### Citations

**File:** libs/cardano-ledger-core/src/Cardano/Ledger/Address.hs (L990-999)
```haskell
-- | Direct deposits to account addresses.
newtype DirectDeposits = DirectDeposits {unDirectDeposits :: Map AccountAddress Coin}
  deriving (Show, Eq, Generic)
  deriving newtype (NoThunks, NFData, EncCBOR, DecCBOR)

instance Semigroup DirectDeposits where
  DirectDeposits d1 <> DirectDeposits d2 = DirectDeposits $ Map.unionWith (<>) d1 d2

instance Monoid DirectDeposits where
  mempty = DirectDeposits Map.empty
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Entities.hs (L211-216)
```haskell
  let directDeposits = tx ^. bodyTxL . directDepositsTxBodyL
      accountsAfterCerts = certStateAfterCerts ^. certDStateL . accountsL
  failOnJust (directDepositsMissingAccounts directDeposits accountsAfterCerts) $
    injectFailure . DirectDepositsToMissingAccounts

  pure $ certStateAfterCerts & certDStateL . accountsL %~ applyDirectDeposits directDeposits
```
