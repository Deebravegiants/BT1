# [?] [mpt] Fix legacy DB upgrade crash from num_cnv_chunks=0 underflow

## Summary
Severity: Unknown
Chain: Monad
Component: monad-crypto/monad
Published: 2026-06-17
Source: https://github.com/category-labs/monad/commit/fdb541ae8135acddaf5a26f7d1222937eeb75a24
Type: security-commit

## Details
[mpt] Fix legacy DB upgrade crash from num_cnv_chunks=0 underflow

DBs created before the num_cnv_chunks footer field existed store 0 there.
storage_pool::device_t::cnv_chunks() returned that raw 0, so
DbMetadataContext::ring_max_chunks_() computed (uint32_t)0 - 1 = 0xFFFFFFFF
and map_ring_storage_ tried to reserve ~exabytes of VA, aborting
monad-mpt --upgrade with an opaque "Assertion 'r != MAP_FAILED'".

Normalize the legacy 0 to the historical default of 3 in cnv_chunks()
itself -- the single source of truth its two callers want; the inline 0->3
fallbacks in fill_chunks_ and the flag-mismatch warning now defer to it.

Add two operator-facing aborts so a genuinely under-provisioned or corrupt
pool fails with an actionable message instead of the opaque mmap assertion:
ring_max_chunks_() rejects pools with fewer than 2 conventional chunks, and
map_ring_storage_ rejects a ring whose recorded length exceeds pool capacity.

Regression test: a footer of 0 (byte-identical to a legacy DB) must open on
both create and reopen; it aborted before this fix.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
