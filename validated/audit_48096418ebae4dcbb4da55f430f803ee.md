### Title
PlutusV4 Sub-Transaction `txInfoFee` Always Hardcoded to `0` in `mkAnyLevelTxInfo` — (File: `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxInfo.hs`)

---

### Summary

In the Dijkstra era's `EraPlutusTxInfo 'PlutusV4 DijkstraEra` instance, the helper `mkAnyLevelTxInfo` unconditionally sets `PV3.txInfoFee = 0`. For top-level transactions this is patched over by `mkTopTxInfo`, which overwrites the field with the real fee. For sub-transactions, `mkSubTxInfo` calls `mkAnyLevelTxInfo` and never overrides the fee, so every PlutusV4 script that inspects a sub-transaction's fee always observes `0`, regardless of the actual lovelace paid.

This is a direct structural analog to the reported `calcMint` bug: a function that should return a computed value derived from its inputs instead returns a hardcoded constant.

---

### Finding Description

`EraPlutusTxInfo 'PlutusV4 DijkstraEra` is implemented in `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxInfo.hs`. The `toPlutusTxInfo` method dispatches on whether the transaction is a top-level or sub-transaction:

```haskell
-- line 500-529
toPlutusTxInfo proxy lti@LedgerTxInfo{..} = do
  withBothTxLevels ltiTx mkTopTxInfo mkSubTxInfo
  where
    mkTopTxInfo tx = PlutusTxInfoResult $ do
      txInfo <- mkAnyLevelTxInfo tx
      let topTxInfo = txInfo {PV3.txInfoFee =
            transCoinToLovelace (tx ^. bodyTxL . feeTxBodyL)}  -- fee FIXED here
      ...
    mkSubTxInfo tx = PlutusTxInfoResult $ do
      txInfo <- mkAnyLevelTxInfo tx
      Right $ \_ -> Right txInfo                               -- fee NOT fixed
```

`mkAnyLevelTxInfo` (lines 530–574) builds the `PV3.TxInfo` record with:

```haskell
-- line 556
PV3.txInfoFee = 0,
```

`mkTopTxInfo` immediately replaces this with the real fee. `mkSubTxInfo` does not, so every sub-transaction's `txInfoFee` is permanently `0` in the `ScriptContext` delivered to any PlutusV4 script.

Additionally, `toPlutusScriptPurpose` for PlutusV4 is a runtime-error stub:

```haskell
-- line 498
toPlutusScriptPurpose _ = error "stub: PlutusV4 not yet implemented"
```

This is called from `toPlutusV4Args` (line 590) whenever a PlutusV4 script is evaluated, meaning any execution of a PlutusV4 script will throw an unchecked Haskell `error`.

---

### Impact Explanation

**`txInfoFee = 0` for sub-transactions (Medium):**

The Dijkstra era introduces sub-transactions guarded by PlutusV4 "guarding scripts." A guarding script is the intended mechanism for a DApp to enforce invariants over sub-transactions, including fee constraints. Because `txInfoFee` is always `0` for sub-transactions, any guarding script that checks `txInfoFee` to bound or verify the fee paid by a sub-transaction will always observe `0` and will approve sub-transactions with arbitrarily large fees. An attacker who is the transaction author can set the sub-transaction fee to any value while the guarding script is deceived into seeing `0`. This allows fees to be manipulated outside design parameters — matching the "Medium" allowed impact: *attacker-controlled transactions modify fees outside design parameters*.

**`toPlutusScriptPurpose` stub (Critical):**

`error` in Haskell throws an impure exception. If this exception propagates outside the evaluation boundary used by the ledger's script-execution harness, it will crash the node process. If different node implementations or versions handle the uncaught exception differently (crash vs. reject), honest nodes may diverge on whether a block containing a PlutusV4 script is valid — matching the "Critical" allowed impact: *honest nodes accept an invalid block or transaction causing permanent ledger divergence requiring a hard fork*.

---

### Likelihood Explanation

**`txInfoFee = 0`:** Any DApp deployed on the Dijkstra era that writes a guarding script checking sub-transaction fees is immediately affected. The attacker is the transaction author — no special privilege is required. Likelihood is high once the era is live.

**`toPlutusScriptPurpose` stub:** Any transaction that includes a PlutusV4 script triggers this path. A single such transaction submitted by any unprivileged user is sufficient to trigger the error. Likelihood is certain once PlutusV4 scripts are used.

---

### Recommendation

1. **Fix `mkAnyLevelTxInfo`**: Remove the hardcoded `PV3.txInfoFee = 0` and instead pass the actual fee as a parameter, or compute it from the transaction body inside `mkAnyLevelTxInfo` directly, so both `mkTopTxInfo` and `mkSubTxInfo` produce correct fee values without relying on a post-hoc override.

2. **Replace the `toPlutusScriptPurpose` stub**: Implement the PlutusV4 script-purpose translation before the Dijkstra era is deployed, or gate PlutusV4 script execution behind a protocol-version check that rejects such transactions with a proper `PredicateFailure` rather than an unchecked `error`.

3. **Address the `_subTxInfosForGuards` TODO** (line 524): The computed sub-transaction infos are discarded and not included in the `ScriptContext` passed to guarding scripts, which means guarding scripts cannot inspect sub-transaction contents at all — a separate but related incompleteness.

---

### Proof of Concept

**`txInfoFee = 0` for sub-transactions:** [1](#0-0) 

The `mkAnyLevelTxInfo` helper hardcodes `PV3.txInfoFee = 0` in the constructed `TxInfo`. [2](#0-1) 

`mkTopTxInfo` overrides this with the real fee at line 506, but `mkSubTxInfo` (lines 527–529) returns `txInfo` unmodified, so sub-transaction fee is always `0`. [3](#0-2) 

**`toPlutusScriptPurpose` stub:** [4](#0-3) 

This stub is invoked from `toPlutusV4Args` which is the `toPlutusArgs` implementation for PlutusV4: [5](#0-4) 

Any transaction containing a PlutusV4 script will call `toPlutusV4Args`, which calls `toPlutusScriptPurpose`, which unconditionally throws a Haskell runtime `error`.

### Citations

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxInfo.hs (L495-499)
```haskell
instance EraPlutusTxInfo 'PlutusV4 DijkstraEra where
  toPlutusTxCert _ _ = pure . transTxCert

  toPlutusScriptPurpose _ = error "stub: PlutusV4 not yet implemented"

```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxInfo.hs (L503-529)
```haskell
      mkTopTxInfo tx = PlutusTxInfoResult $ do
        txInfo <- mkAnyLevelTxInfo tx
        let
          topTxInfo = txInfo {PV3.txInfoFee = transCoinToLovelace (tx ^. bodyTxL . feeTxBodyL)}
        Right $ \case
          purpose@(GuardingPurpose AsPurpose) -> do
            _subTxInfosForGuards <-
              forM (OMap.elems (tx ^. bodyTxL . subTransactionsTxBodyL)) $ \subTx -> do
                let txId = txIdTx subTx
                mkTxInfo <-
                  unPlutusTxInfoResult $
                    case Map.lookup txId (ltiMemoizedSubTransactions lti) of
                      Nothing ->
                        toPlutusTxInfo proxy $
                          lti
                            { ltiTx = subTx
                            , ltiMemoizedSubTransactions = mempty
                            }
                      Just txInfoResults ->
                        lookupTxInfoResult (plutusSLanguage proxy) txInfoResults
                left (SubTxContextError txId) $ mkTxInfo purpose
            -- TODO: Include _subTxInfosForGuards
            Right topTxInfo
          _ -> Right topTxInfo
      mkSubTxInfo tx = PlutusTxInfoResult $ do
        txInfo <- mkAnyLevelTxInfo tx
        Right $ \_ -> Right txInfo
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxInfo.hs (L551-557)
```haskell
        Right $
          PV3.TxInfo
            { PV3.txInfoInputs = inputsInfo
            , PV3.txInfoOutputs = outputs
            , PV3.txInfoReferenceInputs = refInputsInfo
            , PV3.txInfoFee = 0
            , PV3.txInfoMint = Conway.transMintValue (txBody ^. mintTxBodyL)
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxInfo.hs (L580-599)
```haskell
toPlutusV4Args ::
  EraPlutusTxInfo 'PlutusV4 era =>
  proxy 'PlutusV4 ->
  ProtVer ->
  PV3.TxInfo ->
  PlutusPurpose AsIxItem era ->
  Maybe (Data era) ->
  Data era ->
  Either (ContextError era) (PlutusArgs 'PlutusV4)
toPlutusV4Args proxy pv txInfo plutusPurpose maybeSpendingData redeemerData = do
  scriptPurpose <- toPlutusScriptPurpose proxy pv plutusPurpose
  let scriptInfo =
        Conway.scriptPurposeToScriptInfo scriptPurpose (transDatum <$> maybeSpendingData)
  pure $
    PlutusV4Args $
      PV3.ScriptContext
        { PV3.scriptContextTxInfo = txInfo
        , PV3.scriptContextRedeemer = Babbage.transRedeemer redeemerData
        , PV3.scriptContextScriptInfo = scriptInfo
        }
```
