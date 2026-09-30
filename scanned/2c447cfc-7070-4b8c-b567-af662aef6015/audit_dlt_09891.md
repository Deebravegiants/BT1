# [?] fix panic on api.GetBlockMeta (#2413)

## Summary
Severity: Unknown
Chain: IoTeX
Component: iotexproject/iotex-core
Published: 2020-08-21
Source: https://github.com/iotexproject/iotex-core/commit/87a6217be9d5f5952ebbc322f577cb6f18fe8858
Type: security-commit

## Details
fix panic on api.GetBlockMeta (#2413)

## Patch
### api/api.go
```diff
@@ -1168,13 +1168,8 @@ func (api *Server) getBlockMetas(start uint64, count uint64) (*iotexapi.GetBlock
 	}
 	var res []*iotextypes.BlockMeta
 	for height := start; height <= tipHeight && count > 0; height++ {
-		blockMeta, err := api.getBlockMetasByHeader(height)
-		if errors.Cause(err) == db.ErrNotExist {
-			blockMeta, err = api.getBlockMetasByBlock(height)
-			if err != nil {
-				return nil, err
-			}
-		} else if err != nil {
+		blockMeta, err := api.getBlockMetaByHeight(height)
+		if err != nil {
 			return nil, err
 		}
 		res = append(res, blockMeta)
@@ -1192,13 +1187,8 @@ func (api *Server) getBlockMeta(blkHash string) (*iotexapi.GetBlockMetasResponse
 	if err != nil {
 		return nil, status.Error(codes.InvalidArgument, err.Error())
 	}
-	blockMeta, err := api.getBlockMetaByHeader(hash)
-	if errors.Cause(err) == db.ErrNotExist {
-		blockMeta, err = api.getBlockMetaByBlock(hash)
-		if err != nil {
-			return nil, err
-		}
-	} else if err != nil {
+	blockMeta, err := api.getBlockMetaByHash(hash)
+	if err != nil {
 		return nil, err
 	}
 	return &iotexapi.GetBlockMetasResponse{
@@ -1207,6 +1197,28 @@ func (api *Server) getBlockMeta(blkHash string) (*iotexapi.GetBlockMetasResponse
 	}, nil
 }
 
+// getBlockMetaByHeight gets block meta by height
+func (api *Server) getBlockMetaByHeight(height uint64) (*iotextypes.BlockMeta, error) {
+	if api.indexer != nil {
+		blockMeta, err := api.getBlockMetasByHeader(height)
+		if errors.Cause(err) != db.ErrNotExist {
+			return blockMeta, err
+		}
+	}
+	return api.getBlockMetasByBlock(height)
+}
+
+// getBlockMetaByHash gets block meta by hash
+func (api *Server) getBlockMetaByHash(h hash.Hash256) (*iotextypes.BlockMeta, error) {
+	if api.indexer != nil {
+		blockMeta, err := api.getBlockMetaByHeader(h)
+		if errors.Cause(err) != db.ErrNotExist {
+			return blockMeta, err
+		}
+	}
+	return api.getBlockMetaByBlock(h)
+}
+
 // putBlockMetaUpgradeByBlock puts numActions and transferAmount for blockmeta by block
 func (api *Server) putBlockMetaUpgradeByBlock(blk *block.Block, blockMeta *iotextypes.BlockMeta) *iotextypes.BlockMeta {
 	blockMeta.NumActions = int64(len(blk.Actions))
```
