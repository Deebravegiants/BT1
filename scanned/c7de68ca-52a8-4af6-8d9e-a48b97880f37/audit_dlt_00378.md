# [?] [storage] Fix HotState race condition via RCU / deferred merge

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2026-02-18
Source: https://github.com/aptos-labs/aptos-core/commit/fb2d1b124abfa72b6a7115a6a0540e588884177b
Type: security-commit

## Details
[storage] Fix HotState race condition via RCU / deferred merge

069beddb1e0b relaxed assertions so that fork-induced invariant violations
in `StateSummary::update` return errors instead of panicking. That handles
the *summary* path but does not address the underlying data race in
`HotState`: the `Committer` background thread mutates DashMap entries
one-by-one while concurrent readers observe the same DashMaps, and during
a fork the speculative overlay no longer shields readers from those
in-progress mutations.

### The fork scenario

```
         committed          speculative
            |                    |
            v                    v
  ... ─── A ─── B ─── C         (persisted, Committer working here)
            \
             \── B' ── C'        (fork branch, execution reading here)
```

Without a fork, the speculative overlay covers every key the Committer
touches (same blocks, same LRU decisions), so readers never reach the
DashMap for mutated entries. With a fork, `B'/C'` diverge from `B/C`:
the overlay for the fork branch does not cover keys that only changed
on the committed branch. A reader on the fork path falls through the
overlay into the DashMap mid-mutation and can observe:

```
  Committer thread              Reader thread (fork branch)
  ─────────────────             ─────────────────────────
  remove(key_X) from shard
                                 get(key_X.neighbor) -> LRU next = key_X
                                 get(key_X)          -> MISSING!  💥
  insert(key_X) into shard
```

This causes panics in `HotStateLRU::expect_hot_slot()`.

_Trimmed to 38 lines — full report: https://github.com/aptos-labs/aptos-core/commit/fb2d1b124abfa72b6a7115a6a0540e588884177b_
