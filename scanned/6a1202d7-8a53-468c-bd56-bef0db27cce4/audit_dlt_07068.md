# [?] [SharovBot] fix: reduce genesis MDBX map size on Windows to prevent pagefile exhaustion (#19382)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-02-21
Source: https://github.com/erigontech/erigon/commit/84d91b870e706d5741122ca72e004f9f62229735
Type: security-commit

## Details
[SharovBot] fix: reduce genesis MDBX map size on Windows to prevent pagefile exhaustion (#19382)

## Summary

Fixes the reproducible Windows CI failure in
`TestExecutionSpecBlockchain/prague/eip7702_set_code_tx`.

**Failing job:**
https://github.com/erigontech/erigon/actions/runs/22247494407/job/64374046614

## Root Cause

The temporary MDBX database opened in `GenesisToBlock()` was configured
with a **2 TB map size**. This was intentional to support large custom
genesis blocks (e.g., `erigon init` with >1 GB state), but it causes an
immediate crash on Windows:

```
panic: fail to open mdbx: mdbx_env_open: The paging file is too small for this operation to complete.
```

**Why Windows-specific:** On Linux/macOS, MDBX backs large file mappings
with sparse files and copy-on-write pages — only actually-touched pages
consume disk/RAM. On Windows, file-backed mappings (including the
pagefile-backed in-memory ones MDBX uses) must have the **entire map
size reserved** in the system paging file upfront. A 2 TB reservation
far exceeds the CI pagefile minimum of 8 GB, so the `mdbx_env_open` call
fails immediately.

This is not a flaky test — it reproduces every time on any Windows
machine without a >2 TB pagefile.

## Fix

Use **1 GB** as the genesis temp DB map size on Windows. This is:
- Sufficient for any practical genesis block (even very large ones)
- Compatible with the CI pagefile (8 GB minimum, fits even with parallel
test concurrency)
- Preserves the 2 TB ceiling on Linux/macOS where it is harmless

## What Was NOT the Issue

The task description mentioned `setCode=false` in the Prague signer —
but inspecting the current codebase shows that `setCode=true` is
**already correctly set** for Prague in `MakeSigner()`. The `setCode tx
is not supported` log errors visible in the CI logs come from
`CancunToPragueAtTime15k` tests where blocks have timestamps < 15,000
(before Prague activates), which is **expected behavior**. The only real
bug was the MDBX pagefile exhaustion.

## Testing

- `go build ./...` passes ✓
- The fix is platform-conditional: Windows → 1 GB, Linux/macOS → 2 TB
(unchanged)
- On Windows, the genesis temp DB now uses 1 GB, matching the scale of
other test MDBX databases

Closes #19378 (prior PR that documented the issue without fixing it)

Co-authored-by: SharovBot <sharovbot@erigon.ci>

## Patch
### execution/state/genesiswrite/genesis_write.go
```diff
@@ -25,6 +25,7 @@ import (
 	"errors"
 	"fmt"
 	"math/big"
+	"runtime"
 	"slices"
 	"testing"
 
@@ -311,8 +312,17 @@ func GenesisToBlock(tb testing.TB, g *types.Genesis, dirs datadir.Dirs, logger l
 
 	ctx := context.Background()
 
-	// some users creating > 1Gb custome genesis by `erigon init`
-	genesisTmpDB := mdbx.New(dbcfg.TemporaryDB, logger).InMem(tb, dirs.Tmp).MapSize(2 * datasize.TB).GrowthStep(1 * datasize.MB).MustOpen()
+	// some users creating > 1Gb custom genesis by `erigon init`.
+	// On Windows, MDBX file-mappings are backed by the paging file for their full map size,
+	// so a 2 TB reservation immediately exhausts the pagefile when parallel goroutines open
+	// multiple databases (e.g. during test runs). On Linux/macOS the reservation is backed by
+	// sparse files with copy-on-write, so 2 TB is harmless.
+	// 1 GB is plenty for any practical genesis block; the CI pagefile minimum is 8 GB.
+	genesisMapSize := 2 * datasize.TB
+	if runtime.GOOS == "windows" {
+		genesisMapSize = 1 * datasize.GB
+	}
+	genesisTmpDB := mdbx.New(dbcfg.TemporaryDB, logger).InMem(tb, dirs.Tmp).MapSize(genesisMapSize).GrowthStep(1 * datasize.MB).MustOpen()
 	defer genesisTmpDB.Close()
 
 	agg, err := dbstate.New(dirs).Logger(logger).Open(ctx, genesisTmpDB)
```
