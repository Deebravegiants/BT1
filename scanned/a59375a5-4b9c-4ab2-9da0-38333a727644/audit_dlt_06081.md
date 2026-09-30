# [?] fix: data race in signer fields in consortium v2 (#207)

## Summary
Severity: Unknown
Chain: Ronin
Component: axieinfinity/ronin
Published: 2023-02-23
Source: https://github.com/axieinfinity/ronin-archive/commit/d0113ae528ee90efb1b3171a55e00b2599f1634b
Type: security-commit

## Details
fix: data race in signer fields in consortium v2 (#207)

This commit makes all read of signer fields in consortium v2 hold read mutex
lock to synchronize with read mutex lock in Consortium.Authorize function.

## Patch
### consensus/consortium/v2/consortium.go
```diff
@@ -528,7 +528,8 @@ func (c *Consortium) Prepare(chain consensus.ChainHeaderReader, header *types.He
 		return err
 	}
 
-	header.Coinbase = c.val
+	coinbase, _, _ := c.readSigner()
+	header.Coinbase = coinbase
 	header.Nonce = types.BlockNonce{}
 
 	number := header.Number.Uint64()
@@ -538,7 +539,7 @@ func (c *Consortium) Prepare(chain consensus.ChainHeaderReader, header *types.He
 	}
 
 	// Set the correct difficulty
-	header.Difficulty = CalcDifficulty(snap, c.val)
+	header.Difficulty = CalcDifficulty(snap, coinbase)
 
 	// Ensure the extra data has all it's components
 	if len(header.Extra) < extraVanity {
@@ -644,6 +645,7 @@ func (c *Consortium) Finalize(chain consensus.ChainHeaderReader, header *types.H
 	if err := c.initContract(); err != nil {
 		return err
 	}
+	_, _, signTxFn := c.readSigner()
 	evmContext := core.NewEVMBlockContext(header, consortiumCommon.ChainContext{Chain: chain, Consortium: c}, &header.Coinbase, chain.OpEvents()...)
 	transactOpts := &consortiumCommon.ApplyTransactOpts{
 		ApplyMessageOpts: &consortiumCommon.ApplyMessageOpts{
@@ -660,7 +662,7 @@ func (c *Consortium) Finalize(chain consensus.ChainHeaderReader, header *types.H
 		UsedGas:     usedGas,
 		Mining:      false,
 		Signer:      c.signer,
-		SignTxFn:    c.signTxFn,
+		SignTxFn:    signTxFn,
 		EthAPI:      c.ethAPI,
 	}
 
@@ -715,6 +717,7 @@ func (c *Consortium) FinalizeAndAssemble(chain consensus.ChainHeaderReader, head
 	if receipts == nil {
 		receipts = make([]*types.Receipt, 0)
 	}
+	_, _, signTxFn := c.readSigner()
 	evmContext := core.NewEVMBlockContext(header, consortiumCommon.ChainContext{Chain: chain, Consortium: c}, &header.Coinbase, chain.OpEvents()...)
 	transactOpts := &consortiumCommon.ApplyTransactOpts{
 		ApplyMessageOpts: &consortiumCommon.ApplyMessageOpts{
@@ -731,7 +734,7 @@ func (c *Consortium) FinalizeAndAssemble(chain consensus.ChainHeaderReader, head
 		UsedGas:     &header.GasUsed,
 		Mining:      true,
 		Signer:      c.signer,
-		SignTxFn:    c.signTxFn,
+		SignTxFn:    signTxFn,
 	}
 
 	if err := c.processSystemTransactions(chain, header, transactOpts, true); err != nil {
@@ -787,9 +790,7 @@ func (c *Consortium) Seal(chain consensus.ChainHeaderReader, block *types.Block,
 		return nil
 	}
 	// Don't hold the val fields for the entire sealing procedure
-	c.lock.RLock()
-	val, signFn := c.val, c.signFn
-	c.lock.RUnlock()
+	val, signFn, _ := c.readSigner()
 
 	snap, err := c.snapshot(chain, number-1, header.ParentHash, nil)
 	if err != nil {
@@ -875,7 +876,8 @@ func (c *Consortium) CalcDifficulty(chain consensus.ChainHeaderReader, time uint
 	if err != nil {
 		return nil
 	}
-	return CalcDifficulty(snap, c.val)
+	coinbase, _, _ := c.readSigner()
+	return CalcDifficulty(snap, coinbase)
 }
 
 // CalcDifficulty is the difficulty adjustment algorithm. It returns the difficulty
@@ -890,7 +892,8 @@ func CalcDifficulty(snap *Snapshot, signer common.Address) *big.Int {
 
 // initContract creates NewContractIntegrator instance
 func (c *Consortium) initContract() error {
-	contract, err := consortiumCommon.NewContractIntegrator(c.chainConfig, consortiumCommon.NewConsortiumBackend(c.ethAPI), c.signTxFn, c.val)
+	coinbase, _, signTxFn := c.readSigner()
+	contract, err := consortiumCommon.NewContractIntegrator(c.chainConfig, consortiumCommon.NewConsortiumBackend(c.ethAPI), signTxFn, coinbase)
 	if err != nil {
 		return err
 	}
@@ -899,6 +902,13 @@ func (c *Consortium) initContract() error {
 	return nil
 }
 
+func (c *Consortium) readSigner() (common.Address, consortiumCommon.SignerFn, consortiumCommon.SignerTxFn) {
+	c.lock.RLock()
+	defer c.lock.RUnlock()
+
+	return c.val, c.signFn, c.signTxFn
+}
+
 // ecrecover extracts the Ronin account address from a signed header.
 func ecrecover(header *types.Header, sigcache *lru.ARCCache, chainId *big.Int) (common.Address, error) {
 	// If the signature's already cached, return that
```
