# [?] core: fix race condition in WriteMipmapBloom

## Summary
Severity: Unknown
Chain: Scroll
Component: scroll-tech/go-ethereum
Published: 2017-01-09
Source: https://github.com/scroll-tech/go-ethereum/commit/2fed476ce16101e43867b9e2c8cd1625db0180e0
Type: security-commit

## Details
core: fix race condition in WriteMipmapBloom

## Patch
### core/database_util.go
```diff
@@ -23,6 +23,7 @@ import (
 	"errors"
 	"fmt"
 	"math/big"
+	"sync"
 
 	"github.com/ethereum/go-ethereum/common"
 	"github.com/ethereum/go-ethereum/core/types"
@@ -63,6 +64,8 @@ var (
 	oldBlockHashPrefix     = []byte("block-hash-") // [deprecated by the header/block split, remove eventually]
 
 	ChainConfigNotFoundErr = errors.New("ChainConfig not found") // general config not found error
+
+	mipmapBloomMu sync.Mutex // protect against race condition when updating mipmap blooms
 )
 
 // encodeBlockNumber encodes a block number as big endian uint64
@@ -564,6 +567,9 @@ func mipmapKey(num, level uint64) []byte {
 // WriteMapmapBloom writes each address included in the receipts' logs to the
 // MIP bloom bin.
 func WriteMipmapBloom(db ethdb.Database, number uint64, receipts types.Receipts) error {
+	mipmapBloomMu.Lock()
+	defer mipmapBloomMu.Unlock()
+
 	batch := db.NewBatch()
 	for _, level := range MIPMapLevels {
 		key := mipmapKey(number, level)
```
