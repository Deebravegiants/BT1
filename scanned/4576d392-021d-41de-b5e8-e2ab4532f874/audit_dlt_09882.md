# [?] Fix data race for block (#4462)

## Summary
Severity: Unknown
Chain: IoTeX
Component: iotexproject/iotex-core
Published: 2024-10-28
Source: https://github.com/iotexproject/iotex-core/commit/b0ac60b1528db575714624e37eecc5f3d6563758
Type: security-commit

## Details
Fix data race for block (#4462)

## Patch
### blockchain/blockdao/blockdao.go
```diff
@@ -334,13 +334,15 @@ func (dao *blockDAO) PutBlock(ctx context.Context, blk *block.Block) error {
 		}
 	}
 	atomic.StoreUint64(&dao.tipHeight, blk.Height())
-	header := blk.Header
-	hash := blk.HashBlock()
-	lruCachePut(dao.headerCache, blk.Height(), &header)
-	lruCachePut(dao.headerCache, header.HashHeader(), &header)
-	lruCachePut(dao.blockCache, hash, blk)
-	lruCachePut(dao.blockCache, blk.Height(), blk)
 	timer.End()
+	defer func() {
+		header := blk.Header
+		hash := blk.HashBlock()
+		lruCachePut(dao.headerCache, blk.Height(), &header)
+		lruCachePut(dao.headerCache, header.HashHeader(), &header)
+		lruCachePut(dao.blockCache, hash, blk)
+		lruCachePut(dao.blockCache, blk.Height(), blk)
+	}()
 
 	// index the block if there's indexer
 	timer = dao.timerFactory.NewTimer("index_block")
```
