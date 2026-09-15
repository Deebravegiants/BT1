# [?] Fix race condition in backend tests (#1792)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2022-01-12
Source: https://github.com/celo-org/celo-blockchain/commit/3d5160db607445b8a90df942caac366587e1cf45
Type: security-commit

## Details
Fix race condition in backend tests (#1792)

Some tests were failing for example:

=== RUN   TestRecentMessageCaches
panic: runtime error: invalid memory address or nil pointer dereference
[signal SIGSEGV: segmentation violation code=0x1 addr=0x0 pc=0xa07362]

goroutine 1070 [running]:
github.com/celo-org/celo-blockchain/consensus/istanbul/backend.(*Backend).newChainHeadLoop(0xc000881c00, 0xc005cd9400)
	/home/circleci/repos/geth/consensus/istanbul/backend/engine.go:610 +0x82
created by github.com/celo-org/celo-blockchain/consensus/istanbul/backend.(*Backend).SetChain
	/home/circleci/repos/geth/consensus/istanbul/backend/engine.go:599 +0x8c
FAIL	github.com/celo-org/celo-blockchain/consensus/istanbul/backend	79.150s

This Was because go routines started by SetChain were attempting to
subscribe to events on the blockchain event mux after it had been
closed. This was caused by newBlockChain in test_utils.go calling
SetChain and returning both the chain and the engine to the caller,
and in most cases the caller stops the chain, if the stop happened
before the go routines from SetChain had a chance to subscribe then the
above problem would occur.

This PR ensures that the subscriptions now happen in the calling
goroutine thus ensuring that the subscriptions happen before stop can be
called on the chain.
