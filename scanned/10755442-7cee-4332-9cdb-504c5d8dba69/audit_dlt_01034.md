# [H] github.com/ipfs/go-bitswap vulnerable to DOS unbounded persistent memory leak

## Summary
Severity: High
Chain: github.com/ipfs/go-bitswap
Component: github.com/ipfs/go-bitswap
CWE: Uncontrolled Resource Consumption, Allocation of Resources Without Limits or Throttling
Published: 2023-05-11
Source: https://github.com/advisories/GHSA-q3j6-22wf-3jh9
Type: github-advisory

## Details
This package has been moved to [`github.com/ipfs/boxo/bitswap`](https://pkg.go.dev/github.com/ipfs/boxo/bitswap), this vulnerability is tracked there: https://github.com/ipfs/boxo/security/advisories/GHSA-m974-xj4j-7qv5 (`CVE-2023-25568`)

### Remediation
This is a two step process:
1. Apply one of:
   - (**recommended**) upgrade from `github.com/ipfs/go-bitswap` to `github.com/ipfs/boxo/bitswap`.
   - If you are still using `github.com/ipfs/go-bitswap` and cannot upgrade to `boxo`, you can upgrade to `github.com/ipfs/go-bitswap@v0.12.0`, this will replace the `go-bitswap` implementation by stubs which points to `boxo`.
2. Open https://github.com/ipfs/boxo/security/advisories/GHSA-m974-xj4j-7qv5 and then follow `boxo`'s remediation section.

### Vulnerable symbols
- `>= v0.9.0; < v0.12.0`
  - `github.com/ipfs/go-bitswap/server/internal/decision.(*Engine).MessageReceived`
  - `github.com/ipfs/go-bitswap/server/internal/decision.(*Engine).NotifyNewBlocks`
  - `github.com/ipfs/go-bitswap/server/internal/decision.(*Engine).findOrCreate`
  - `github.com/ipfs/go-bitswap/server/internal/decision.(*Engine).PeerConnected`
- `v0.8.0`
  - `github.com/ipfs/go-bitswap/internal/decision.(*Engine).MessageReceived`
  - `github.com/ipfs/go-bitswap/internal/decision.(*Engine).NotifyNewBlocks`
  - `github.com/ipfs/go-bitswap/internal/decision.(*Engine).findOrCreate`
  - `github.com/ipfs/go-bitswap/internal/decision.(*Engine).PeerConnected`
- `< v0.8.0`
  - `github.com/ipfs/go-bitswap/internal/decision.(*Engine).MessageReceived`
  - `github.com/ipfs/go-bitswap/internal/decision.(*Engine).receiveBlocksFrom`
  - `github.com/ipfs/go-bitswap/internal/decision.(*Engine).findOrCreate`
  - `github.com/ipfs/go-bitswap/internal/decision.(*Engine).PeerConnected`

### Workarounds
If you are using the stubs at `github.com/ipfs/go-bitswap` and not taking advantage of the features provided by the server, refactoring your code to use the new split API will allows you to run in a client-only mode using: [`github.com/ipfs/go-bitswap/client`](https://pkg.go.dev/github.com/ipfs/go-bitswap/client).
