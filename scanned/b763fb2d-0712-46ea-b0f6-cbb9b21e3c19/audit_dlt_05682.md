# [?] Fix other current (round state) data race

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2021-09-22
Source: https://github.com/celo-org/celo-blockchain/commit/f2f2ef1f2f8c1cb754a0758c54ba11eee70817ba
Type: security-commit

## Details
Fix other current (round state) data race

The current round state of the engine was being read without
synchronisation via core.CurrentView by the miner the current round
state was also being written in the engines stop function.

The fix is to use the pre-existing mutex to syncronise accesses through
CurrentView.

==================
WARNING: DATA RACE
Read at 0x00c000bb20b8 by goroutine 506:
  github.com/celo-org/celo-blockchain/consensus/istanbul/core.(*core).CurrentView()
      /home/pierspowlesland/projects/celo-blockchain/consensus/istanbul/core/core.go:195 +0x4a
  github.com/celo-org/celo-blockchain/consensus/istanbul/backend.waitCoreToReachSequence()
      /home/pierspowlesland/projects/celo-blockchain/consensus/istanbul/backend/engine.go:1203 +0x24c
  github.com/celo-org/celo-blockchain/consensus/istanbul/backend.(*Backend).addParentSeal.func1()
      /home/pierspowlesland/projects/celo-blockchain/consensus/istanbul/backend/engine.go:982 +0x130
  github.com/celo-org/celo-blockchain/consensus/istanbul/backend.(*Backend).addParentSeal()
      /home/pierspowlesland/projects/celo-blockchain/consensus/istanbul/backend/engine.go:1019 +0x3ab
  github.com/celo-org/celo-blockchain/consensus/istanbul/backend.(*Backend).Prepare()
      /home/pierspowlesland/projects/celo-blockchain/consensus/istanbul/backend/engine.go:404 +0x404
  github.com/celo-org/celo-blockchain/miner.prepareBlock()
      /home/pierspowlesland/projects/celo-blockchain/miner/block.go:89 +0x62f
  github.com/celo-org/celo-blockchain/miner.(*worker).constructAndSubmitNewBlock()
      /home/pierspowlesland/projects/celo-blockchain/miner/worker.go:242 +0x84
  github.com/celo-org/celo-blockchain/miner.(*worker).mainLoop.func1.1()
      /home/pierspowlesland/projects/celo-blockchain/miner/worker.go:379 +0x5c

Previous write at 0x00c000bb20b8 by goroutine 93:
  github.com/celo-org/celo-blockchain/consensus/istanbul/core.(*core).Stop()
      /home/pierspowlesland/projects/celo-blockchain/consensus/istanbul/core/handler.go:67 +0x8e
  github.com/celo-org/celo-blockchain/consensus/istanbul/backend.(*Backend).StopValidating()
      /home/pierspowlesland/projects/celo-blockchain/consensus/istanbul/backend/engine.go:707 +0x193
  github.com/celo-org/celo-blockchain/miner.(*worker).stop()
      /home/pierspowlesland/projects/celo-blockchain/miner/worker.go:220 +0xbb
  github.com/celo-org/celo-blockchain/miner.(*Miner).update()
      /home/pierspowlesland/projects/celo-blockchain/miner/miner.go:173 +0x6fb
