# [?] fix(avm): avoid data race on shared interaction selector writes (#24456)

## Summary
Severity: Unknown
Chain: Aztec
Component: AztecProtocol/aztec-packages
Published: 2026-07-02
Source: https://github.com/AztecProtocol/aztec-packages/commit/e3f3a1464577b3b4d0371e1ad9fa5203da3becd3
Type: security-commit

## Details
fix(avm): avoid data race on shared interaction selector writes (#24456)

## What was wrong

The interactions tracegen phase runs every lookup/permutation job
concurrently: `AvmTraceGenHelper::fill_trace_interactions` concatenates
all builders' jobs and dispatches them with `parallel_for`. Lookups
whose fine-grained destination selector is a *shared* column
(`DST_SELECTOR != outer_dst_selector`) can resolve to the same `dst_row`
from different jobs, so multiple threads write the same `(selector,
row)` cell at once.

The previous code did a guarded read-modify-write on that shared cell:

```cpp
if (DST_SELECTOR != outer_dst_selector && trace.get(DST_SELECTOR, dst_row) != 1) {
    trace.set(DST_SELECTOR, dst_row, 1);
}
```

Both the `get` and the non-atomic 32-byte `set` race against the other
threads' writes to the same cell — a data race, i.e. undefined behavior.
In practice it produced the right value (every writer stores `1`), but
it is still UB.

## The fix

Add an opt-in `use_atomic_limbs` flag to `TraceContainer::set`. When
set, the field's four 64-bit limbs are written with **relaxed atomic
stores** — four plain `movq` on x86-64, no lock and no libatomic call.
(A whole-field `std::atomic_ref<FF>` is *not* an option on the hot path:
at 32 bytes it exceeds the hardware lock-free width and falls back to a
locked libatomic call.)

The shared selector write now uses it and drops the guard read:

```cpp
if (DST_SELECTOR != outer_dst_selector) {
    trace.set(DST_SELECTOR, dst_row, 1, /*use_atomic_limbs=*/true);
}
```

The write is an unconditional, idempotent atomic store of `1`. Because
every concurrent writer stores the *same* value, per-limb atomicity is
sufficient — no torn value is possible — so this is data-race-free
without the cost of whole-field atomicity. The default (non-atomic)
`set` hot path is untouched and keeps its sparse-column "zero = absent"
fast path.

## Performance (this PR vs baseline)

Mega bulk AVM tx, full proving, `HARDWARE_CONCURRENCY=16`. Tracegen
stage timings, median of runs (baseline n=3, this PR n=6):

| Stage | baseline (`next`) | this PR |
|---|---|---|
| tracegen traces | 1,536 ms | 1,537 ms |
| tracegen interactions | 350 ms | 329 ms |
| tracegen all | 1,917 ms | 1,936 ms |

No measurable cost — the safety fix is free. The per-limb atomic only
fires on the shared selector writes in the interactions stage; the
traces stage is byte-for-byte the same hot path as baseline.

Fixes
https://linear.app/aztec-labs/issue/AVM-276/interactions-tracegen-does-ub-write-to-destination-selector

### barretenberg/cpp/src/barretenberg/vm2/tracegen/lib/lookup_builder.hpp
```diff
@@ -51,10 +51,10 @@ template <typename LookupSettings_> class IndexedLookupTraceBuilder : public Int
             }
 
             trace.set(LookupSettings::COUNTS, dst_row, trace.get(LookupSettings::COUNTS, dst_row) + 1);
-            // Set the fine grained inner selector if it's not already one.
-            if (LookupSettings::DST_SELECTOR != this->outer_dst_selector &&
-                trace.get(LookupSettings::DST_SELECTOR, dst_row) != 1) {
-                trace.set(LookupSettings::DST_SELECTOR, dst_row, 1);
+            if (LookupSettings::DST_SELECTOR != this->outer_dst_selector) {
+                // This step might write to the same cell from multiple threads, so we use atomic limbs to avoid UB.
+                // Since we are always writing a 1, the end result will be 1 even under concurrency.
+                trace.set(LookupSettings::DST_SELECTOR, dst_row, 1, /*use_atomic_limbs=*/true);
             }
         });
     }
@@ -198,10 +198,10 @@ template <typename LookupSettings> class LookupIntoDynamicTableSequential : publ
                 if (dst_selector == 1 && src_values == trace.get_multiple(LookupSettings::DST_COLUMNS, dst_row)) {
                     trace.set(LookupSettings::COUNTS, dst_row, trace.get(LookupSettings::COUNTS, dst_row) + 1);
 
-                    // Set the fine grained inner selector if it's not already one.
-                    if (LookupSettings::DST_SELECTOR != this->outer_dst_selector &&
-                        trace.get(LookupSettings::DST_SELECTOR, dst_row) != 1) {
-                        trace.set(LookupSettings::DST_SELECTOR, dst_row, 1);
+                    if (LookupSettings::DST_SELECTOR != this->outer_dst_selector) {
+                        // This step might write to the same cell from multiple threads, so we use atomic limbs to avoid
+                        // UB. Since we are always writing a 1, the end result will be 1 even under concurrency.
+                        trace.set(LookupSettings::DST_SELECTOR, dst_row, 1, /*use_atomic_limbs=*/true);
                     }
 
                     found = true;
```

### barretenberg/cpp/src/barretenberg/vm2/tracegen/trace_container.cpp
```diff
@@ -4,6 +4,7 @@
 #include <ranges>
 
 #include "barretenberg/common/assert.hpp"
+#include "barretenberg/common/compiler_hints.hpp"
 #include "barretenberg/common/log.hpp"
 #include "barretenberg/common/ref_vector.hpp"
 #include "barretenberg/vm2/common/field.hpp"
@@ -13,7 +14,19 @@ namespace bb::avm2::tracegen {
 namespace {
 
 // We need a zero value to return (a reference to) when a value is not found.
-static const FF zero = FF::zero();
+const FF zero = FF::zero();
+
+// Writes each 64-bit limb of the field with a relaxed atomic store. Each limb is naturally aligned (FF is
+// alignas(32), 4x uint64_t), so this lowers to 4 plain `movq` stores on x86-64 — no lock, no libatomic call
+// (unlike a whole-field std::atomic_ref<FF>, whose 32 bytes exceed the lock-free width). Lets set() make a
+// same-cell concurrent write data-race-free when every writer stores the same value.
+inline void store_per_limb(FF& cell, const FF& value)
+{
+    static_assert(sizeof(FF) == 4 * sizeof(uint64_t));
+    for (size_t i = 0; i < 4; ++i) {
+        std::atomic_ref<uint64_t>(cell.data[i]).store(value.data[i], std::memory_order_relaxed);
+    }
+}
 
 } // namespace
 
@@ -62,7 +75,7 @@ TraceContainer::ColumnInterval& TraceContainer::get_or_create_shard(SparseColumn
     return *expected; // CAS failure loaded the winning pointer into `expected` (acquire).
 }
 
-void TraceContainer::set(Column col, uint32_t row, const FF& value)
+void TraceContainer::set(Column col, uint32_t row, const FF& value, bool use_atomic_limbs)
 {
     auto& column_data = (*trace)[static_cast<size_t>(col)];
     const size_t shard_idx = row / INTERVAL_SIZE;
@@ -73,12 +86,22 @@ void TraceContainer::set(Column col, uint32_t row, const FF& value)
         // Lock-free: a single atomic load finds the shard (created on first write), then we write our
         // own dense cell directly. Different rows are distinct array elements, so concurrent writers of
         // this column (or even of the same shard, at a chunk boundary) never race and never serialize.
-        get_or_create_shard(column_data, shard_idx).rows[offset] = value;
+        auto& cell = get_or_create_shard(column_data, shard_idx).rows[offset];
+        if (BB_UNLIKELY(use_atomic_limbs)) {
+            store_per_limb(cell, value);
+        } else {
+            cell = value;
+        }
     } else {
-        // Zero value: clear if present. We never create a shard (clearing an absent row is a no-op).
+        // Zero value: clear if present. We never create a shard, so sparse (mostly-zero) columns are not
+        // materialized (an unset cell already reads as zero).
         ColumnInterval* shard = column_data.slots[shard_idx].load(std::memory_order_acquire);
         if (shard != nullptr) {
-            shard->rows[offset] = FF::zero();
+            if (BB_UNLIKELY(use_atomic_limbs)) {
+                store_per_limb(shard->rows[offset], zero);
+            } else {
+                shard->rows[offset] = FF::zero();
+            }
         }
     }
 }
```

### barretenberg/cpp/src/barretenberg/vm2/tracegen/trace_container.hpp
```diff
@@ -76,7 +76,11 @@ class TraceContainer {
     // Extended version of get that works with shifted columns. More expensive.
     const FF& get_column_or_shift(ColumnAndShifts col, uint32_t row) const;
 
-    void set(Column col, uint32_t row, const FF& value);
+    // Sets the value of a cell. Thread-safe if the same cell is not written to from multiple threads.
+    // If writing to the same cell from multiple threads, use_atomic_limbs=true to use atomic limbs.
+    // This makes the write slower, but it will not be UB. However, it is also not thread-safe.
+    // Use only if you know what you are doing.
+    void set(Column col, uint32_t row, const FF& value, bool use_atomic_limbs = false);
     // Bulk setting for a given row.
     void set(uint32_t row, std::span<const std::pair<Column, FF>> values);
     // Reserve column size. Useful for precomputed columns.
```
