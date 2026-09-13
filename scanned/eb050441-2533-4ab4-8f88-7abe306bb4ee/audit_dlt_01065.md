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

**step 1** -  start the rendezvous server (uses the example from the repo):
```bash
cargo run --manifest-path examples/rendezvous/Cargo.toml --bin rendezvous-example
```

**step 2** -  run the flood client (attached as `rzv-flood.rs`):
```bash
cargo run --manifest-path examples/rendezvous/Cargo.toml --bin rzv-flood
```

it connects as a single peer and registers 10,000 unique namespaces (`flood-00000000` through `flood-00009999`), chaining each registration on the confirmed `Registered` event from the previous one.

server accepted every single one. not one rejection.

memory on the server side (via `ps aux` RSS column):

```
baseline:       ~18 MB
mid flood:      ~26 MB  
after 10k regs: ~28 MB
```

that's from one peer. scale to 100 sybil peers doing the same thing and you're looking at ~1GB. 1000 peers and the server is dead.

<img width="1032" height="124" alt="image" src="https://github.com/user-attachments/assets/f778f179-2aa1-4485-940c-25e218733fa8" />

*server RSS climbing during the flood*

<img width="553" height="760" alt="image" src="https://github.com/user-attachments/assets/691b0f52-dda0-443f-a3c2-98c8c6336f2f" />

*10,000 registrations confirmed, zero rejected*



### Impact

any node running libp2p-rendezvous server-side is affected. rendezvous servers are typically well-known, publicly reachable nodes  taking one down disrupts peer discovery for all clients depending on it. any rust-libp2p based project that deploys a rendezvous point is at risk.

no special position on the network needed. no crypto work. just open a connection and send REGISTER in a loop.

## **Researchers**

**Discovered by:**
- Ramesh Adhikari (CoE-CNDS Lab, VJTI, Mumbai, India)
- Dr. Faruk Kazi (CoE-CNDS Lab, VJTI, Mumbai, India)



**Organization:** Centre of Excellence in Complex & Nonlinear Dynamical Systems (CoE-CNDS Lab), Veermata Jijabai Technological Institute (VJTI), Mumbai, India

---

We have not disclosed this to any other vendor or made it public. We are reporting directly to the [rust-libp2p](https://github.com/libp2p/rust-libp2p) security team through this advisory.
