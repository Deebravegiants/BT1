# [?] fix(tx): add IsExpired, to prevent potential uint32 overflow

## Summary
Severity: Unknown
Chain: VeChain
Component: vechain/thor
Published: 2018-04-18
Source: https://github.com/vechain/thor/commit/05d4a33217367be5af2d3adf5fae4c6f4c6d0754
Type: security-commit

## Details
fix(tx): add IsExpired, to prevent potential uint32 overflow

## Patch
### consensus/validate.go
```diff
@@ -108,7 +108,7 @@ func (c *Consensus) validateBlockBody(blk *block.Block) error {
 			return errors.New("bad tx: chain tag mismatch")
 		case header.Number() < tx.BlockRef().Number():
 			return errors.New("bad tx: ref blcok too new")
-		case header.Number() > tx.BlockRef().Number()+tx.Expiration():
+		case tx.IsExpired(header.Number()):
 			return errors.New("bad tx: expired")
 		case tx.HasReservedFields():
 			return errors.New("bad tx: reserved fields not empty")
```

### packer/packer.go
```diff
@@ -96,7 +96,7 @@ func (p *Packer) Prepare(parent *block.Header, nowTimestamp uint64) (
 				return badTxError{"reserved fields not empty"}
 			case parent.Number()+1 < tx.BlockRef().Number():
 				return errTxNotAdoptableNow
-			case parent.Number()+1 > tx.BlockRef().Number()+tx.Expiration():
+			case tx.IsExpired(parent.Number() + 1):
 				return badTxError{"expired"}
 			case totalGasUsed+tx.Gas() > gasLimit:
 				// gasUsed < 90% gas limit
```

### tx/transaction.go
```diff
@@ -76,6 +76,11 @@ func (t *Transaction) Expiration() uint32 {
 	return t.body.Expiration
 }
 
+// IsExpired returns whether the tx is expired according to the given blockNum.
+func (t *Transaction) IsExpired(blockNum uint32) bool {
+	return uint64(blockNum) > uint64(t.BlockRef().Number())+uint64(t.body.Expiration) // cast to uint64 to prevent potential overflow
+}
+
 // ID returns id of tx.
 // ID = hash(signingHash, signer).
 // It returns zero Bytes32 if signer not available.
```

### txpool/txpool.go
```diff
@@ -163,7 +163,7 @@ func (pool *TxPool) pendingObjs(bestBlock *block.Block, shouldSort bool) txObjec
 	var pendings txObjects
 	for id, obj := range all {
 		tx := obj.Tx()
-		if tx.Expiration()+tx.BlockRef().Number() < bestBlock.Header().Number() || time.Now().Unix()-obj.CreationTime() > int64(pool.config.Lifetime) {
+		if tx.IsExpired(bestBlock.Header().Number()) || time.Now().Unix()-obj.CreationTime() > int64(pool.config.Lifetime) {
 			pool.Remove(id)
 			continue
 		}
@@ -230,7 +230,7 @@ func (pool *TxPool) update(bestBlock *block.Block) {
 	//can be pendinged txObjects
 	for id, obj := range all {
 		tx := obj.Tx()
-		if tx.Expiration()+tx.BlockRef().Number() < bestBlock.Header().Number() || time.Now().Unix()-obj.CreationTime() > int64(pool.config.Lifetime) {
+		if tx.IsExpired(bestBlock.Header().Number()) || time.Now().Unix()-obj.CreationTime() > int64(pool.config.Lifetime) {
 			pool.Remove(id)
 			continue
 		}
```
