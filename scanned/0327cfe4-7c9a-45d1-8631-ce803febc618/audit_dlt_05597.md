# [?] p2p/enode: fix discovery AyncFilter deadlock on shutdown (#32572)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2025-10-02
Source: https://github.com/ethereum/go-ethereum/commit/f0dc47aae393abe0bb7b084345daf9108ad8897a
Type: security-commit

## Details
p2p/enode: fix discovery AyncFilter deadlock on shutdown (#32572)

Description:
We found a occasionally node hang issue on BSC, I think Geth may
also have the issue, so pick the fix patch here.
The fix on BSC repo: https://github.com/bnb-chain/bsc/pull/3347

When the hang occurs, there are two routines stuck.
- routine 1: AsyncFilter(...)
On node start, it will run part of the DiscoveryV4 protocol, which could
take considerable time, here is its hang callstack:
```
goroutine 9711 [chan receive]:  // this routine was stuck on read channel: `<-f.slots`
github.com/ethereum/go-ethereum/p2p/enode.AsyncFilter.func1()
	github.com/ethereum/go-ethereum/p2p/enode/iter.go:206 +0x125
created by github.com/ethereum/go-ethereum/p2p/enode.AsyncFilter in goroutine 1
	github.com/ethereum/go-ethereum/p2p/enode/iter.go:192 +0x205

```

- Routine 2: Node Stop
It is the main routine to shutdown the process, but it got stuck when it
tries to shutdown the discovery components, as it tries to drain the
channel of `<-f.slots`, but the extra 1 slot will never have chance to
be resumed.
```
goroutine 11796 [chan receive]: 
github.com/ethereum/go-ethereum/p2p/enode.(*asyncFilterIter).Close.func1()
	github.com/ethereum/go-ethereum/p2p/enode/iter.go:248 +0x5c
sync.(*Once).doSlow(0xc032a97cb8?, 0xc032a97d18?)
	sync/once.go:78 +0xab
sync.(*Once).Do(...)
	sync/once.go:69
github.com/ethereum/go-ethereum/p2p/enode.(*asyncFilterIter).Close(0xc092ff8d00?)
	github.com/ethereum/go-ethereum/p2p/enode/iter.go:244 +0x36
github.com/ethereum/go-ethereum/p2p/enode.(*bufferIter).Close.func1()
	github.com/ethereum/go-ethereum/p2p/enode/iter.go:299 +0x24
sync.(*Once).doSlow(0x11a175f?, 0x2bfe63e?)
```

_Trimmed to 38 lines — full report: https://github.com/ethereum/go-ethereum/commit/f0dc47aae393abe0bb7b084345daf9108ad8897a_
