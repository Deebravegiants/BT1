# [?] fix: await processFn to prevent buffer pool race condition (#8877)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ChainSafe/lodestar
Published: 2026-02-07
Source: https://github.com/ChainSafe/lodestar/commit/b87b37f4d02b01f5e9fa0bf87adce318888ed40b
Type: security-commit

## Details
fix: await processFn to prevent buffer pool race condition (#8877)

## Motivation

Fixes a race condition that can cause state corruption and `First offset
must equal to fixedEnd` errors on restart.

See discussion:
https://discord.com/channels/593655374469660673/1469368525180113078

## Description

The `using` keyword in `serializeState.ts` releases the buffer back to
the pool when the block exits. Since `processFn` is async (returns a
Promise), the buffer was being released before the DB write completed.

If another serialization (checkpoint state or archive state) happened
before the write finished, it would:
1. Get the same buffer from the pool
2. Call `fill(0)` on it (per BufferPool.alloc behavior)
3. Corrupt the data being written by the first serialization

This could cause `First offset must equal to fixedEnd 0 != <large
number>` errors on restart when the corrupted state is read.

## Fix

Add `await` before `processFn(stateBytes)` to ensure the buffer is not
released until the async operation completes.

---

**AI Disclosure:** This PR was authored with AI assistance
(Lodekeeper/Claude).

Co-authored-by: lodekeeper <lodekeeper@users.noreply.github.com>
