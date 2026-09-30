# [?] db: fix integer overflow vulnerability in FixedSizeBitmapsWriter (#17073)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2025-11-21
Source: https://github.com/erigontech/erigon/commit/ee62d9c9371f4178903553691a18e47735894afd
Type: security-commit

## Details
db: fix integer overflow vulnerability in FixedSizeBitmapsWriter (#17073)

Replace unsafe `multiplication` with` math.SafeMul()` in bitmap size
calculation.

Fixes the TODO

Co-authored-by: Alexey Sharov <AskAlexSharov@gmail.com>

## Patch
### db/kv/bitmapdb/fixed_size_bitmaps.go
```diff
@@ -26,12 +26,12 @@ import (
 	"time"
 	"unsafe"
 
-	"github.com/erigontech/erigon/common/dir"
-
 	"github.com/c2h5oh/datasize"
 	mmap2 "github.com/edsrzf/mmap-go"
 
+	"github.com/erigontech/erigon/common/dir"
 	"github.com/erigontech/erigon/common/log/v3"
+	"github.com/erigontech/erigon/common/math"
 )
 
 type FixedSizeBitmaps struct {
@@ -222,8 +222,11 @@ const MetaHeaderSize = 64
 func NewFixedSizeBitmapsWriter(indexFile string, bitsPerBitmap int, baseDataID, amount uint64, logger log.Logger) (*FixedSizeBitmapsWriter, error) {
 	pageSize := os.Getpagesize()
 	_, fileName := filepath.Split(indexFile)
-	//TODO: use math.SafeMul()
-	bytesAmount := MetaHeaderSize + (bitsPerBitmap*int(amount))/8 + 1
+	bitsTotal, overflow := math.SafeMul(uint64(bitsPerBitmap), amount)
+	if overflow {
+		return nil, fmt.Errorf("overflow when calculating total bits: %d * %d", bitsPerBitmap, amount)
+	}
+	bytesAmount := MetaHeaderSize + int(bitsTotal)/8 + 1
 	size := (bytesAmount/pageSize + 1) * pageSize // must be page-size-aligned
 	idx := &FixedSizeBitmapsWriter{
 		indexFile:      indexFile,
```
