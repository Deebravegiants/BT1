# [?] fix(storage): make flash area bounds checks overflow-safe

## Summary
Severity: Unknown
Chain: Trezor
Component: trezor/trezor-firmware
Published: 2026-08-13
Source: https://github.com/trezor/trezor-firmware/commit/aeda2a30f13bdf3766539080b63c76e56223cdd7
Type: security-commit

## Details
fix(storage): make flash area bounds checks overflow-safe

Both bounds checks added an offset to a size in `uint32_t` before comparing
against the limit:

  flash_area_get_address():      offset + size <= subarea_size
  flash_area_write_data_padded(): offset + total_size > flash_area_get_size()

A sufficiently large second operand wraps the sum to a small value, so the
comparison passes and the function reports the range as fitting. Rewrite both
as subtractions, which cannot wrap. In `flash_area_get_address()` the
subtraction cannot underflow either, since the enclosing condition has already
established that the offset is below the sub-area size.

Neither check is reachable with such arguments today. The address lookup is
gated by `offset < subarea_size` first, so wrapping needs an almost 4 GB size
rather than a large offset, and no caller passes one - `secret_read()` is not
exposed as a syscall and every one of its call sites uses a constant or a
range-checked length. The padded write is backed by `get_sector_and_offset()`,
which re-derives the sector for every block written and fails for an offset
past the area. Both checks are nonetheless the documented bound that a future
caller would reasonably trust.

[no changelog]

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>

## Patch
### storage/flash_area.c
```diff
@@ -70,8 +70,10 @@ const void *flash_area_get_address(const flash_area_t *area, uint32_t offset,
     uint32_t subarea_size = flash_sector_size(first_sector, num_sectors);
     // Does the requested block start in the sub-area?
     if (offset < subarea_size) {
-      // Does the requested block fit in the sub-area?
-      if (offset + size <= subarea_size) {
+      // Does the requested block fit in the sub-area? Written as a subtraction
+      // so that a large `size` cannot wrap the sum past the limit. The
+      // subtraction cannot underflow, `offset` is below `subarea_size` here.
+      if (size <= subarea_size - offset) {
         const uint8_t *ptr =
             (const uint8_t *)flash_get_address(first_sector, 0, 0);
         // We expect that all sectors/pages in the sub-area make
@@ -155,7 +157,9 @@ secbool __wur flash_area_write_data_padded(const flash_area_t *area,
   if (data_size > total_size) {
     return secfalse;
   }
-  if (offset + total_size > flash_area_get_size(area)) {
+  // Written as a subtraction so that the sum cannot wrap past the area size
+  const uint32_t area_size = flash_area_get_size(area);
+  if (offset > area_size || total_size > area_size - offset) {
     return secfalse;
   }
 
```
