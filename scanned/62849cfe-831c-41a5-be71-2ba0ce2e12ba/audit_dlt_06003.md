# [?] eth: fix potential data race

## Summary
Severity: Unknown
Chain: Ethereum Classic
Component: etclabscore/core-geth
Published: 2024-03-12
Source: https://github.com/etclabscore/core-geth/commit/0880c5f74b29036bc3e0f2f445bc7bbb1e38b690
Type: security-commit

## Details
eth: fix potential data race

> go test -race ./eth
...
WARNING: DATA RACE
Read at 0x00000268c128 by goroutine 10750:
  github.com/ethereum/go-ethereum/eth.(*chainSyncer).nextSyncOp()
      /home/ia/go/src/github.com/ethereum/go-ethereum/eth/sync.go:204 +0x216
  github.com/ethereum/go-ethereum/eth.(*chainSyncer).loop()
      /home/ia/go/src/github.com/ethereum/go-ethereum/eth/sync.go:146 +0x3f3
  github.com/ethereum/go-ethereum/eth.(*handler).Start.func3()
      /home/ia/go/src/github.com/ethereum/go-ethereum/eth/handler.go:604 +0x33

Previous write at 0x00000268c128 by goroutine 8683:
  github.com/ethereum/go-ethereum/eth.TestArtificialFinalityFeatureEnablingDisabling_StaleHead()
      /home/ia/go/src/github.com/ethereum/go-ethereum/eth/sync_test.go:344 +0x16a
  testing.tRunner()
      /home/ia/go1.21.2.linux-amd64/go/src/testing/testing.go:1595 +0x238
  testing.(*T).Run.func1()
      /home/ia/go1.21.2.linux-amd64/go/src/testing/testing.go:1648 +0x44

Date: 2024-03-12 11:33:33-06:00
Signed-off-by: meows <b5c6@protonmail.com>
