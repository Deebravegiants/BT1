# [H] libp2p-rendezvous: Unlimited namespace registrations per peer enables OOM DoS on rendezvous servers

## Summary
Severity: High
Chain: libp2p-rendezvous
Component: libp2p-rendezvous
CVE: CVE-2026-35405
CWE: Allocation of Resources Without Limits or Throttling
Published: 2026-04-04
Source: https://github.com/advisories/GHSA-cqfx-gf56-8x59
Type: github-advisory

## Details
### Summary
found that `libp2p-rendezvous` server has no limit on how many namespaces a single peer can register. a malicious peer can just keep registering unique namespaces in a loop and the server happily accepts every single one  allocating memory for each registration with no pushback. keep doing this long enough (or with multiple sybil peers) and the server process gets OOM killed.

no auth required. any peer on the network can do this.



### Details

the bug is in `Registrations::add()` inside `protocols/rendezvous/src/server.rs`.

the store uses a BiMap keyed on `(PeerId, Namespace)`  so yes, a peer can't register the *same* namespace twice. but there's nothing stopping it from registering 10,000 *different* namespaces. each unique one gets its own entry in:

- `registrations_for_peer` (BiMap)
- `registrations` (HashMap)
- `next_expiry` (FuturesUnordered  a new heap-allocated BoxFuture per registration)

namespace strings are only validated for length (`MAX_NAMESPACE = 255`), not count. there's no `max_registrations_per_peer` anywhere in `Config` or the rest of the codebase.

making it worse  `MAX_TTL = 72 hours`. so every registration just sits there for up to 3 days. disconnecting doesn't clean anything up either, entries only go away when the TTL fires.

```
protocols/rendezvous/src/server.rs
  └── Registrations::add()   ← no per-peer count check anywhere

protocols/rendezvous/src/lib.rs
  ├── MAX_NAMESPACE = 255    ← length capped, count is not
  └── MAX_TTL = 72h          ← entries persist a long time
```

fix would be adding something like `max_registrations_per_peer` to `Config` and checking it at the top of `add()` before inserting anything.



### PoC

tested on `libp2p v0.56.1`, built from source.


_Trimmed to 38 lines — full report: https://github.com/advisories/GHSA-cqfx-gf56-8x59_
