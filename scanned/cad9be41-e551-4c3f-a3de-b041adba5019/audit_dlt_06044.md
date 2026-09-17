# [?] kaiax/gov: fix nil-header panic when rebuilding gov/vote cache

## Summary
Severity: Unknown
Chain: Kaia
Component: kaiachain/kaia
Published: 2026-06-18
Source: https://github.com/kaiachain/kaia/commit/66f6fd1eddbdba1073626e012e162d4733d95d41
Type: security-commit

## Details
kaiax/gov: fix nil-header panic when rebuilding gov/vote cache

readGovDataFromDB/readVoteDataFromDB dereferenced headers fetched from the
persisted gov/vote block-number index without a nil check, panicking on every
startup when the index and header DB diverged — for example when the index
lists a block above the current head that is no longer canonical. Since the
same index is read on each restart, this could become a restart loop.

Skip a block whose header is above the current head; a missing header at or
below the head means the canonical chain is broken and is fatal. The shared
loop is extracted into forEachIndexedHeader. The in-memory cache is recomputed
on every startup, so the stale index is left untouched.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
