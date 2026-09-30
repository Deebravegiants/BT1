# [?] core/txpool: added nil checks to prevent crash in stateless mode (#1961)

## Summary
Severity: Unknown
Chain: Polygon
Component: 0xPolygon/bor
Published: 2026-01-02
Source: https://github.com/0xPolygon/bor/commit/0131c7bba7f853d6215cb8fe2cab8437805643e3
Type: security-commit

## Details
core/txpool: added nil checks to prevent crash in stateless mode (#1961)

## Patch
### core/txpool/txpool.go
```diff
@@ -300,6 +300,9 @@ func (p *TxPool) Get(hash common.Hash) *types.Transaction {
 
 // GetRLP returns a RLP-encoded transaction if it is contained in the pool.
 func (p *TxPool) GetRLP(hash common.Hash) []byte {
+	if p == nil {
+		return nil
+	}
 	for _, subpool := range p.subpools {
 		encoded := subpool.GetRLP(hash)
 		if len(encoded) != 0 {
@@ -312,6 +315,9 @@ func (p *TxPool) GetRLP(hash common.Hash) []byte {
 // GetMetadata returns the transaction type and transaction size with the given
 // hash.
 func (p *TxPool) GetMetadata(hash common.Hash) *TxMetadata {
+	if p == nil {
+		return nil
+	}
 	for _, subpool := range p.subpools {
 		if meta := subpool.GetMetadata(hash); meta != nil {
 			return meta
@@ -425,6 +431,9 @@ func (p *TxPool) PoolNonce(addr common.Address) uint64 {
 // Nonce returns the next nonce of an account at the current chain head. Unlike
 // PoolNonce, this function does not account for pending executable transactions.
 func (p *TxPool) Nonce(addr common.Address) uint64 {
+	if p == nil {
+		return 0
+	}
 	p.stateLock.RLock()
 	defer p.stateLock.RUnlock()
 
@@ -450,6 +459,9 @@ func (p *TxPool) Stats() (int, int) {
 // Content retrieves the data content of the transaction pool, returning all the
 // pending as well as queued transactions, grouped by account and sorted by nonce.
 func (p *TxPool) Content() (map[common.Address][]*types.Transaction, map[common.Address][]*types.Transaction) {
+	if p == nil {
+		return make(map[common.Address][]*types.Transaction), make(map[common.Address][]*types.Transaction)
+	}
 	var (
 		runnable = make(map[common.Address][]*types.Transaction)
 		blocked  = make(map[common.Address][]*types.Transaction)
@@ -470,6 +482,9 @@ func (p *TxPool) Content() (map[common.Address][]*types.Transaction, map[common.
 // ContentFrom retrieves the data content of the transaction pool, returning the
 // pending as well as queued transactions of this address, grouped by nonce.
 func (p *TxPool) ContentFrom(addr common.Address) ([]*types.Transaction, []*types.Transaction) {
+	if p == nil {
+		return []*types.Transaction{}, []*types.Transaction{}
+	}
 	for _, subpool := range p.subpools {
 		run, block := subpool.ContentFrom(addr)
 		if len(run) != 0 || len(block) != 0 {
```

### eth/backend.go
```diff
@@ -384,10 +384,6 @@ func New(stack *node.Node, config *ethconfig.Config) (*Ethereum, error) {
 		eth.txPool.SetGasTip(new(big.Int).SetUint64(params.BorDefaultTxPoolPriceLimit))
 	}
 
-	// The `config.TxPool.PriceLimit` used above doesn't reflect the sanitized/enforced changes
-	// made in the txpool. Update the `gasTip` explicitly to reflect the enforced value.
-	eth.txPool.SetGasTip(new(big.Int).SetUint64(params.BorDefaultTxPoolPriceLimit))
-
 	if !config.TxPool.NoLocals {
 		rejournal := config.TxPool.Rejournal
 		if rejournal < time.Second {
```
