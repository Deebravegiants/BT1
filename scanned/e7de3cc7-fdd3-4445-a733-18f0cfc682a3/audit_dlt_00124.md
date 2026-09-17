# [H] kubo: malformed blocks terminate the daemon

## Summary
Severity: High
Chain: IPFS
Component: ipfs/kubo
CWE: Uncaught Exception, Improper Handling of Exceptional Conditions, Allocation of Resources Without Limits or Throttling
Published: 2026-08-11
Source: https://github.com/ipfs/kubo/security/advisories/GHSA-jrj5-c86r-47x2
Type: github-advisory

## Details
A remote, unauthenticated HTTP request for a small malformed block could terminate the
Kubo daemon or exhaust its memory. The default gateway is affected, and no configuration
change is needed to be exposed.

## Details

Kubo decodes and encodes blocks on goroutines detached from the request in three of its
own commands: `ls`, `dag get` and `dag export`. Go's per-request recovery does not reach a
bare goroutine, so a panic raised while decoding an attacker's block ended the daemon
instead of failing the command.

```go
go func() {
    lsErr <- api.Unixfs().Ls(...)   // no recover(): a panic here ends the process
}()
```

The panics that reach those goroutines come from the block decoders Kubo links. Each is
recorded separately:

- Git object parsing: GHSA-fxcw-q88c-xc56, GHSA-9954-gxx9-5j62, GHSA-8vrj-pgm5-fm2h. Kubo
  preloads the `ipldgit` plugin, so the git-raw codec is registered by default.
- UnixFS sharded directories: GHSA-x448-5hh2-3q44.
- boxo's gateway, which had the same containment gap on its own CAR traversal goroutine,
  plus unbounded traversal depth: GHSA-f7qp-w5gp-j382, GHSA-mj62-2x95-pcpr.

The blocks are content addressed and self consistent, so an attacker controls the CID
because it is the hash of bytes they chose. A gateway asked for that CID fetches it from
them and decodes it.

## Proof of concept

Verified against `v0.43.0-rc1` with two nodes, the victim's blockstore empty:

| Request | Result |
|---|---|
| `GET /ipfs/<git-raw cid>?format=car` | daemon terminated |
| `Accept: application/vnd.ipld.car` on the same path | daemon terminated |
| `POST /api/v0/dag/export` | daemon terminated |
| `POST /api/v0/ls` on a crafted shard | daemon terminated |
| Gateway directory listing of a nested crafted shard | daemon terminated |
| `GET /ipfs/<16-byte block declaring 2 GB>?format=car` | RSS 63 MB to 1972 MiB |
| `GET /ipfs/<18-byte block declaring 100 GB>?format=car` | daemon killed |

Under a memory limit, which is what any container or cgroup deployment has, the
allocation ends in `fatal error: out of memory`. That is a Go runtime throw, not a panic,
so no recovery can contain it.

Smallest payloads: 14 bytes for the git tag variant, 18 bytes for the memory case, 75
bytes for the HAMT case.

## Impact

Any Kubo node whose gateway or RPC API is reachable by an attacker. Availability only: no
confidentiality or integrity impact.

Public gateway operators are the primary exposure. The gateway listens by default and the
CAR format is part of the trustless gateway surface, so `Gateway.DeserializedResponses`
does not prevent it.

The RPC API binds to localhost by default, so `/api/v0/ls` and `/api/v0/dag/export` matter
where the API is exposed, or where a local application passes user-supplied CIDs to it,
which pinning services and desktop apps commonly do.

## Patches

Upgrade to [v0.43.0](https://github.com/ipfs/kubo/releases/tag/v0.43.0).

https://github.com/ipfs/kubo/pull/11409 adds recovery to the `ls`, `dag get` and
`dag export` goroutines. The same release pulls in the decoder fixes:

- `go-ipld-git` [v0.1.3](https://github.com/ipfs/go-ipld-git/releases/tag/v0.1.3)
- `go-unixfsnode` [v1.10.6](https://github.com/ipfs/go-unixfsnode/releases/tag/v1.10.6)
- `boxo` [v0.42.1](https://github.com/ipfs/boxo/releases/tag/v0.42.1)

## Workarounds

Upgrading is the only measure that covers every entry point.

[`Gateway.NoFetch=true`](https://github.com/ipfs/kubo/blob/v0.43.0/docs/config.md#gatewaynofetch)
closes the gateway path on an unpatched node. The gateway's blockservice is then built
with an offline exchange, so the daemon never retrieves the attacker's block and never
decodes it. Three limits:

- It does not cover the RPC API. The `Gateway.NoFetch` value is only consulted when the
  CoreAPI is built for the gateway, so `/api/v0/ls`, `/api/v0/dag/get` and
  `/api/v0/dag/export` still fetch.
- It does not help when the block is already in the local blockstore, which covers any
  node that ingests content from its users.
- It turns the gateway into one that serves only what it already holds.

Two settings that look like mitigations and are not:

- `Gateway.DeserializedResponses=false` does not help. The CAR format is part of the
  trustless gateway surface, so `?format=car` is served on exactly that configuration.
- `Plugins.Plugins.ipld-git.Disabled=true` does not help. `go-ipld-git` registers its
  codec into go-ipld-prime's global registry from a package `init()`, so linking the
  package is enough to make it reachable. The flag only skips the plugin's own
  `Register()` call.

Operators who cannot upgrade immediately can reduce the blast radius by running the daemon
under a process supervisor that restarts it, and by placing a memory limit on the
container so an out-of-memory kill is bounded and local.

## Severity rationale

Attack Complexity is Low because the payloads are fixed byte strings, repeatable, with no
race or timing dependence, and the attacker controls the CID since it is the hash of their
own bytes.

Availability is High because the daemon terminates and stops serving every other request,
rather than returning an error for the offending one.
