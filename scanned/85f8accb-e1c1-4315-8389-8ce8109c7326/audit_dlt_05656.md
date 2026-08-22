# [?] Fix/addtrustedpeer empty addrs panic (#16757)

## Summary
Severity: Unknown
Chain: Ethereum
Component: prysmaticlabs/prysm
Published: 2026-06-29
Source: https://github.com/OffchainLabs/prysm/commit/1d4007b60cb56becd64360ccdd28e616face7971
Type: security-commit

## Details
Fix/addtrustedpeer empty addrs panic (#16757)

**What type of PR is this?**

Bug fix


**What does this PR do? Why is it needed?**

`AddTrustedPeer` parses a peer multiaddr and then indexes
`info.Addrs[0]` without checking whether any transport address was
present. A peer-only multiaddr such as `/p2p/<peer_id>` can parse
successfully while producing an `AddrInfo` with an empty `Addrs` slice.
The unchecked index then panics. The same pattern also exists in
`connectWithAllTrustedPeers`.

This PR fixes this by:
- Added a length check after parsing the address in `AddTrustedPeer`.
- Skipped peers that have no dialable address before indexing `Addrs[0]`
in `connectWithAllTrustedPeers` and `peerIdsFromMultiAddrs`.
- Added `TestAddTrustedPeer_NoTransportAddress` to verify the handler
returns `400 Bad Request` instead of panicking.

**Which issue(s) does this PR fix?**

None.

**Other notes for review**

The test results before the fix:
```
$ go test ./beacon-chain/rpc/prysm/node -run '^TestAddTrustedPeer_NoTransportAddress$' -count=1
--- FAIL: TestAddTrustedPeer_NoTransportAddress (0.00s)
panic: runtime error: index out of range [0] with length 0 [recovered, repanicked]

goroutine 307 [running]:
testing.tRunner.func1.2({0x1a3d860, 0xc0000547e0})
        /home/alleysira/go/pkg/mod/golang.org/toolchain@v0.0.1-go1.25.1.linux-amd64/src/testing/testing.go:1872 +0x237
```

_Trimmed to 38 lines — full report: https://github.com/OffchainLabs/prysm/commit/1d4007b60cb56becd64360ccdd28e616face7971_
