# [?] Fix data race on p2p peer purposes

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2021-09-22
Source: https://github.com/celo-org/celo-blockchain/commit/3c44dfe13cc733f45778040f9de4c8e78ba92e05
Type: security-commit

## Details
Fix data race on p2p peer purposes

p2p.PurposeFlag is not threadsafe but was being accessed from many
go-routines without syncronisation via p2p.Peer.HasPurpose.

The solution was to lock over the access in HasPurpose using the mutex
that already existed to synchronise access to a peer's purposes flag.

==================
WARNING: DATA RACE
Read at 0x00c001520680 by goroutine 291:
  github.com/celo-org/celo-blockchain/p2p.(*Peer).HasPurpose()
      /home/pierspowlesland/projects/celo-blockchain/p2p/peer.go:167 +0x5fd
  github.com/celo-org/celo-blockchain/eth.(*peer).PurposeIsSet()
      /home/pierspowlesland/projects/celo-blockchain/eth/peer.go:696 +0x516
  github.com/celo-org/celo-blockchain/eth.(*ProtocolManager).FindPeers()
      /home/pierspowlesland/projects/celo-blockchain/eth/handler.go:1055 +0x612
  github.com/celo-org/celo-blockchain/consensus/istanbul/backend.(*validatorPeerHandler).ReplaceValidatorPeers()
      /home/pierspowlesland/projects/celo-blockchain/consensus/istanbul/backend/peer_handler.go:147 +0x201
  github.com/celo-org/celo-blockchain/consensus/istanbul/backend/internal/enodes.(*ValidatorEnodeDB).RefreshValPeers()
      /home/pierspowlesland/projects/celo-blockchain/consensus/istanbul/backend/internal/enodes/val_enode_db.go:480 +0x641
  github.com/celo-org/celo-blockchain/consensus/istanbul/backend.(*Backend).RefreshValPeers()
      /home/pierspowlesland/projects/celo-blockchain/consensus/istanbul/backend/backend.go:846 +0x264
  github.com/celo-org/celo-blockchain/consensus/istanbul/backend.(*Backend).StartValidating()
      /home/pierspowlesland/projects/celo-blockchain/consensus/istanbul/backend/engine.go:691 +0x3a5
  github.com/celo-org/celo-blockchain/miner.(*worker).start()
      /home/pierspowlesland/projects/celo-blockchain/miner/worker.go:210 +0x1a2
  github.com/celo-org/celo-blockchain/miner.(*Miner).update()
      /home/pierspowlesland/projects/celo-blockchain/miner/miner.go:161 +0x6a4

Previous write at 0x00c001520680 by goroutine 343:
  github.com/celo-org/celo-blockchain/p2p.(*Peer).AddPurpose()
      /home/pierspowlesland/projects/celo-blockchain/p2p/peer.go:148 +0xd5
  github.com/celo-org/celo-blockchain/p2p.(*Server).run.func3()
      /home/pierspowlesland/projects/celo-blockchain/p2p/server.go:866 +0x2d1
  github.com/celo-org/celo-blockchain/p2p.(*Server).run()
      /home/pierspowlesland/projects/celo-blockchain/p2p/server.go:916 +0x241a
