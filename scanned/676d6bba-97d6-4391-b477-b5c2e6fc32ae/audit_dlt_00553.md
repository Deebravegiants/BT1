# [?] common/race: fix darwin -race crashes from file mmaps in the TSAN heap window (#21611)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-07-09
Source: https://github.com/erigontech/erigon/commit/c9b6aed3971fbaf511e84d6076d9b86f16fe54a3
Type: security-commit

## Details
common/race: fix darwin -race crashes from file mmaps in the TSAN heap window (#21611)

## Problem

`go test -race` on darwin (Apple Silicon) flakily dies in mdbx-heavy
packages — reproduced at **6/6** on `main` with `EXEC3_PARALLEL=true go
test -race ./execution/execmodule ./execution/state` on an M-series Mac
— with either of:

```
fatal error: runtime: split stack overflow        (sigpanic → racecall, no DATA RACE report)
fatal error: too many address space collisions for -race mode
```

The same packages pass the Linux race CI legs, which long disguised this
as an environment flake. It isn't — both fatals share one root cause.

## Root cause (caught live in lldb)

Catching the original fault under lldb (before the Go runtime mangles it
into "split stack overflow") shows:

```
thread #26, stop reason = EXC_BAD_ACCESS (code=1, address=0x21882000bbb0)
  frame #0: __tsan_read + 44
  frame #2: txnprovider/txpool.(*TxPool).fromDB
(lldb) memory region `($x1 - 0x200000000000)/2`     ← app address for that shadow
[0x000000c410004000-0x000000c810000000) r--          ← a 16GiB mdbx data map
(lldb) memory region $x1                             ← its TSAN shadow
[0x21884800bbb0-0x219a00000000) ---                  ← unmapped
```

1. Go's race-mode heap lives in TSAN's Go/darwin window `[0x00c0…,
0x00e0…)`; shadow (`shadow = app*2 + 0x2000_0000_0000`) is mapped **per
heap arena**.
2. Each in-mem test env reserves a **16GiB** VA map (`InMem` geometry
upper bound); with dozens of parallel testers the kernel's bottom-up
placement exhausts low VA and drops mdbx maps **between Go heap
arenas**.
3. The runtime's `racecalladdr` validity filter checks one coarse
interval `[racearenastart, racearenaend)` (min/max over arenas) — a
sandwiched map passes the check with no shadow → the first instrumented
read (txpool `fromDB`) faults inside `__tsan_read`. The SEGV lands while
`racecall` is on the g0 stack, so the runtime dies with the misleading
split-stack throw. The same squatting also makes heap-arena reservation
collide repeatedly → the "too many address space collisions" fatal.

Linux is unaffected because `mmap(NULL)` there places file maps near
`0x7f…`, far from the heap window, so they always fail the
`racecalladdr` filter and are simply (silently) invisible to TSAN.

Two repair strategies were tried and rejected with evidence before the
final one:
- **Calling the runtime's own `__tsan_map_shadow` per mapping**
verifiably does nothing here: compiler-rt's Go-mode `MapShadow` tracks a
monotonic `ctx->mapped_shadow_*` interval and silently `return`s for
requests inside it — interior holes (precisely this case) are skipped.
Confirmed in compiler-rt source and empirically (crash inside a region
the call had "covered").
- **Direct shadow mmaps per mdbx env / per `unix.Mmap`**, locating
regions via `mach_vm_region` + `proc_regionfilename`, fixed the crash
but serialized an O(all-VM-regions) walk into every env open —
`execution/tests` (thousands of env opens) went from 9 minutes to a 1h
timeout.

## Fix

`common/race` (linked via blank imports from `db/kv/mdbx` and
`common/mmap`; everything is compiled out unless `race && darwin`):

- At init, fill every unmapped gap in the heap window's shadow
`[app*2+0x2000…, …)` with zeroed `MAP_FIXED|MAP_ANON|MAP_NORESERVE`
mappings, leaving existing arena shadow untouched. One-time cost of a
few mmaps; zero per-open cost; covers every file mapping the kernel ever
places in the window — current or future, mdbx or otherwise. Zero shadow
is valid "no prior access" TSAN state, so races on such mappings also
become *detectable* where they were previously fatal — for plain
reads/writes; Go atomics on such mappings would still fault, since meta
shadow is not pre-mapped.
- The hard-coded layout (window bounds + shadow formula) is self-checked
at init against a live heap allocation (it must be in-window with mapped
shadow); on mismatch the package disables itself with a warning,
restoring old behavior.

Plus: `InMem` test geometry **16GiB → 1GiB** upper bound (only when a
`testing.TB` is supplied, and not for benchmarks, which run sequentially
and can need the full map). Unit tests never approach 1GiB per env; this
removes the TB-scale VA squatting that pushes file maps into the heap
window in the first place and is what triggers the "address space
collisions" fatal.

## Verification

- Repro rate of `EXEC3_PARALLEL=true go test -race
./execution/execmodule ./execution/state` (sequential, quiet M-series
machine): `main` **6/6 fatal** → this branch **0/8**.
- `EXEC3_PARALLEL=true go test -race ./execution/tests` completes in
normal time (the rejected per-open design hung it — kept as a regression
gate).
- `go test -race ./common/race`: asserts the layout self-check and that
shadow is actually mapped across the whole window.
- Full `EXEC3_PARALLEL=true go test -race ./execution/...` green —
re-verified after merging main (2026-07-08, `-count=1`: 52 ok / 0 fail);
`make lint` clean; `make erigon integration` builds; stubs cross-compile
(linux/windows).
- The post-merge sweep initially caught `./execution/engineapi` dying
**6/6** with the "address space collisions" fatal — a sibling mechanism,
not a regression of this fix: the txpool DB's hard-coded **1TB**
geometry (`txnprovider/txpool/assemble.go`) cannot fit below the 768GiB
heap-window base on darwin, so each tester node's txpool map spanned the
window (caught live in vmmap: two 1TB `txpool/mdbx.dat` maps starting
320MB above the window base) and burned the runtime's 32 race-mode arena
hints, which are discarded permanently on collision; the fatal then hits
a later innocent allocation. Fixed by flowing the tester's existing 1GB
`MdbxDBSizeLimit` into the txpool config: **6/6 fatal → 6/6 green**.
Linux is unaffected (top-down mmap places the reservation near `0x7f…`).

TDD note: natural occurrence depends on kernel VM placement (hence the
flakiness), but the crash is deterministically reproducible —
golang/go#80292 carries a standalone ~50-line reproducer (mmap with an
address hint into the heap window + heap ballast + one instrumented
read, 100% fatal). In-repo, a deterministic crash test would need a
separate crashing subprocess (the fault kills the whole test binary), so
the unit test pins the fix's load-bearing properties (layout constants,
window coverage) and the repetition harness above is the end-to-end
gate; each design iteration was validated live in lldb.

This is arguably a Go runtime/TSAN deficiency (coarse interval in
`racecalladdr`, interior-skip in Go-mode `MapShadow`) — reported
upstream as golang/go#80292 with a deterministic standalone reproducer;
this PR makes erigon's macOS race runs work today.

Forensics trail: first reported as a suspected environment flake on
#21605
(https://github.com/erigontech/erigon/pull/21605#issuecomment-4612637589).

### common/mmap/mmap_unix.go
```diff
@@ -27,6 +27,8 @@ import (
 	"unsafe"
 
 	"golang.org/x/sys/unix"
+
+	_ "github.com/erigontech/erigon/common/race"
 )
 
 const MaxMapSize = 0xFFFFFFFFFFFF
```

### common/race/shadow_darwin.go
```diff
@@ -0,0 +1,125 @@
+// Copyright 2026 The Erigon Authors
+// This file is part of Erigon.
+//
+// Erigon is free software: you can redistribute it and/or modify
+// it under the terms of the GNU Lesser General Public License as published by
+// the Free Software Foundation, either version 3 of the License, or
+// (at your option) any later version.
+//
+// Erigon is distributed in the hope that it will be useful,
+// but WITHOUT ANY WARRANTY; without even the implied warranty of
+// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
+// GNU Lesser General Public License for more details.
+//
+// You should have received a copy of the GNU Lesser General Public License
+// along with Erigon. If not, see <http://www.gnu.org/licenses/>.
+
+//go:build race && darwin
+
+// Package race provides the Enabled constant and, on darwin, a workaround
+// for https://go.dev/issue/80292: file mappings that the kernel places
+// between Go heap arenas have no TSAN shadow, so the first instrumented
+// access kills the runtime ("fatal error: runtime: split stack overflow").
+// At init this package pre-maps zeroed shadow over every hole in the heap
+// window's shadow range — data shadow only, so Go atomics on such mappings
+// would still fault on unmapped meta shadow.
+package race
+
+/*
+#include <mach/mach.h>
+#include <mach/mach_vm.h>
+#include <stdint.h>
+#include <sys/mman.h>
+#include <unistd.h>
+
+static int shadow_is_mapped(uint64_t shadow_addr) {
+	mach_vm_address_t q = shadow_addr;
+	mach_vm_size_t size = 0;
+	vm_region_basic_info_data_64_t info;
+	mach_msg_type_number_t count = VM_REGION_BASIC_INFO_COUNT_64;
+	mach_port_t object_name = MACH_PORT_NULL;
+	kern_return_t kr = mach_vm_region(mach_task_self(), &q, &size, VM_REGION_BASIC_INFO_64,
+		(vm_region_info_t)&info, &count, &object_name);
+	if (object_name != MACH_PORT_NULL) {
+		mach_port_deallocate(mach_task_self(), object_name);
+	}
+	return kr == KERN_SUCCESS && q <= shadow_addr && (info.protection & VM_PROT_READ) != 0;
+}
+
+// map_shadow_holes mmaps zeroed shadow into the unmapped gaps of the shadow
+// range [sbeg, send), leaving already-mapped shadow untouched.
+static int map_shadow_holes(uint64_t sbeg, uint64_t send) {
+	long page = sysconf(_SC_PAGESIZE);
+	if (page <= 0) {
+		return -1;
+	}
+	uint64_t mask = ~(uint64_t)(page - 1);
+	sbeg &= mask;
+	send = (send + page - 1) & mask;
+	uint64_t addr = sbeg;
+	while (addr < send) {
+		mach_vm_address_t q = addr;
+		mach_vm_size_t size = 0;
+		vm_region_basic_info_data_64_t info;
+		mach_msg_type_number_t count = VM_REGION_BASIC_INFO_COUNT_64;
+		mach_port_t object_name = MACH_PORT_NULL;
+		kern_return_t kr = mach_vm_region(mach_task_self(), &q, &size, VM_REGION_BASIC_INFO_64,
+			(vm_region_info_t)&info, &count, &object_name);
+		if (object_name != MACH_PORT_NULL) {
+			mach_port_deallocate(mach_task_self(), object_name);
+		}
+		uint64_t hole_end = (kr == KERN_SUCCESS && q < send) ? q : send;
+		if (hole_end > addr) {
+			void *p = mmap((void *)addr, hole_end-addr, PROT_READ|PROT_WRITE,
+				MAP_FIXED|MAP_PRIVATE|MAP_ANON|MAP_NORESERVE, -1, 0);
+			if (p == MAP_FAILED) {
+				return -1;
+			}
+		}
+		if (kr != KERN_SUCCESS || q >= send) {
+			break;
+		}
+		addr = q + size;
+	}
+	return 0;
+}
+*/
+import "C"
+
+import (
+	"fmt"
+	"os"
+	"unsafe"
+)
+
+// TSAN's Go/darwin heap window; raceinit places arenas here.
+const heapWindowBeg, heapWindowEnd = 0x00c0_0000_0000, 0x00e0_0000_0000
+
+// enabled records that the layout self-check passed and the window's shadow
+// holes were filled at init.
+var enabled bool
+
+// heapProbe is package-level so it is heap-allocated regardless of escape
+// analysis; the init self-check tests the TSAN layout against its address.
+var heapProbe = new([16]byte)
+
+func init() {
+	probe := uintptr(unsafe.Pointer(heapProbe))
+	if probe < heapWindowBeg || probe >= heapWindowEnd ||
+		C.shadow_is_mapped(C.uint64_t(mem2shadow(probe))) == 0 {
+		fmt.Fprintln(os.Stderr, "race: TSAN shadow layout self-check failed; not pre-mapping shadow for the heap window")
+		return
+	}
+	sbeg, send := mem2shadow(heapWindowBeg), mem2shadow(heapWindowEnd)
+	enabled = C.map_shadow_holes(C.uint64_t(sbeg), C.uint64_t(send)) == 0
+	if !enabled {
+		fmt.Fprintln(os.Stderr, "race: pre-mapping TSAN shadow for the heap window failed")
+	}
+}
+
+func mem2shadow(addr uintptr) uintptr { return addr*2 + 0x2000_0000_0000 }
+
+// shadowIsMapped reports whether the shadow for addr is mapped (test hook).
+func shadowIsMapped(addr uintptr) bool {
+	return C.shadow_is_mapped(C.uint64_t(mem2shadow(addr))) != 0
+}
```

### common/race/shadow_darwin_test.go
```diff
@@ -0,0 +1,35 @@
+// Copyright 2026 The Erigon Authors
+// This file is part of Erigon.
+//
+// Erigon is free software: you can redistribute it and/or modify
+// it under the terms of the GNU Lesser General Public License as published by
+// the Free Software Foundation, either version 3 of the License, or
+// (at your option) any later version.
+//
+// Erigon is distributed in the hope that it will be useful,
+// but WITHOUT ANY WARRANTY; without even the implied warranty of
+// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
+// GNU Lesser General Public License for more details.
+//
+// You should have received a copy of the GNU Lesser General Public License
+// along with Erigon. If not, see <http://www.gnu.org/licenses/>.
+
+//go:build race && darwin
+
+package race
+
+import (
+	"testing"
+
+	"github.com/stretchr/testify/require"
+)
+
+func TestHeapWindowShadowPreMapped(t *testing.T) {
+	require.True(t, enabled, "TSAN Go/darwin shadow layout changed — update mem2shadow/heapWindow")
+
+	// Shadow must be mapped across the whole heap window, so any file mapping
+	// the kernel later places between Go arenas is readable by __tsan_read.
+	for _, addr := range []uintptr{heapWindowBeg, (heapWindowBeg + heapWindowEnd) / 2, heapWindowEnd - 8} {
+		require.True(t, shadowIsMapped(addr), "shadow unmapped for window addr %#x", addr)
+	}
+}
```

### common/race/shadow_fallback.go
```diff
@@ -0,0 +1,21 @@
+// Copyright 2026 The Erigon Authors
+// This file is part of Erigon.
+//
+// Erigon is free software: you can redistribute it and/or modify
+// it under the terms of the GNU Lesser General Public License as published by
+// the Free Software Foundation, either version 3 of the License, or
+// (at your option) any later version.
+//
+// Erigon is distributed in the hope that it will be useful,
+// but WITHOUT ANY WARRANTY; without even the implied warranty of
+// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
+// GNU Lesser General Public License for more details.
+//
+// You should have received a copy of the GNU Lesser General Public License
+// along with Erigon. If not, see <http://www.gnu.org/licenses/>.
+
+//go:build !race || !darwin
+
+// Package race provides the Enabled constant and, on darwin race builds, a
+// workaround for https://go.dev/issue/80292; see shadow_darwin.go.
+package race
```

### db/kv/mdbx/kv_mdbx.go
```diff
@@ -42,6 +42,7 @@ import (
 	"github.com/erigontech/erigon/common/dir"
 	"github.com/erigontech/erigon/common/estimate"
 	"github.com/erigontech/erigon/common/log/v3"
+	_ "github.com/erigontech/erigon/common/race"
 	"github.com/erigontech/erigon/db/kv"
 	"github.com/erigontech/erigon/db/kv/dbcfg"
 	"github.com/erigontech/erigon/db/kv/order"
@@ -177,6 +178,12 @@ func (opts MdbxOpts) InMem(tb testing.TB, tmpDir string) MdbxOpts {
 	opts.dirtySpace = uint64(16 * datasize.MB)
 	if tb != nil {
 		opts.dirtySpace = uint64(2 * datasize.MB)
+		// Parallel unit tests pile 16GB VA reservations into the Go race heap
+		// window ("too many address space collisions for -race mode"); cap them.
+		// Benchmarks run sequentially and can need the full map.
+		if _, isBench := tb.(*testing.B); !isBench {
+			opts.mapSize = 1 * datasize.GB
+		}
 	}
 	opts.shrinkThreshold = 0 // disable
 	opts.pageSize = 4096
```

### execution/engineapi/engineapitester/engine_api_tester.go
```diff
@@ -280,6 +280,10 @@ func InitialiseEngineApiTester(ctx context.Context, args EngineApiTesterInitArgs
 	txPoolConfig := txpoolcfg.DefaultConfig
 	txPoolConfig.DBDir = dirs.TxPool
 	txPoolConfig.Disable = args.DisableTxPool
+	// Without a limit the txpool DB reserves 1TB of VA, which cannot fit below
+	// the Go race-mode heap window on darwin and starves arena reservation
+	// ("too many address space collisions for -race mode").
+	txPoolConfig.MdbxDBSizeLimit = mdbxDBSizeLimit
 	syncDefault := ethconfig.Defaults.Sync
 	syncDefault.ParallelStateFlushing = false
 	ethConfig := ethconfig.Config{
```
