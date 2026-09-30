# [?] avoid pointer arithmetic overflow

## Summary
Severity: Unknown
Chain: EOS/Vaulta
Component: AntelopeIO/leap
Published: 2024-03-08
Source: https://github.com/AntelopeIO/leap/commit/f2111dbef37b4b52536bb67100f72840057ac634
Type: security-commit

## Details
avoid pointer arithmetic overflow

## Patch
### libraries/chain/webassembly/runtimes/eos-vm-oc/memory.cpp
```diff
@@ -40,7 +40,7 @@ memory::memory(uint64_t sliced_pages) {
    uintptr_t* const intrinsic_jump_table = reinterpret_cast<uintptr_t* const>(zeropage_base - first_intrinsic_offset);
    const intrinsic_map_t& intrinsics = get_intrinsic_map();
    for(const auto& intrinsic : intrinsics)
-      intrinsic_jump_table[-intrinsic.second.ordinal] = (uintptr_t)intrinsic.second.function_ptr;
+      intrinsic_jump_table[-(int)intrinsic.second.ordinal] = (uintptr_t)intrinsic.second.function_ptr;
 }
 
 memory::~memory() {
```
