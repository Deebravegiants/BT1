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

_Trimmed to 38 lines — full report: https://github.com/ipfs/kubo/security/advisories/GHSA-jrj5-c86r-47x2_
