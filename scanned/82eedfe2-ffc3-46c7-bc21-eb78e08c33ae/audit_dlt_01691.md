# [?] Fix race condition around consensus state (#81)

## Summary
Severity: Unknown
Chain: Sei
Component: sei-protocol/sei-chain
Published: 2023-03-10
Source: https://github.com/sei-protocol/sei-chain/commit/5a62cf502a847c47c42dd2f4d75c203926b7cce1
Type: security-commit

## Details
Fix race condition around consensus state (#81)

* Fix race condition around consensus state

* Remove write lock since we already acquired it earlier

* Fix lock

---------

Co-authored-by: Yiming Zang <yzang@twitter.com>

## Patch
### sei-tendermint/internal/consensus/reactor.go
```diff
@@ -777,15 +777,18 @@ func (r *Reactor) gossipVotesRoutine(ctx context.Context, ps *PeerState, voteCh
 
 		// catchup logic -- if peer is lagging by more than 1, send Commit
 		blockStoreBase := r.state.blockStore.Base()
+
 		if blockStoreBase > 0 && prs.Height != 0 && rs.Height >= prs.Height+2 && prs.Height >= blockStoreBase {
 			// Load the block's extended commit for prs.Height, which contains precommit
 			// signatures for prs.Height.
 			var ec *types.ExtendedCommit
+			r.state.mtx.RLock()
 			if r.state.state.ConsensusParams.ABCI.VoteExtensionsEnabled(prs.Height) {
 				ec = r.state.blockStore.LoadBlockExtendedCommit(prs.Height)
 			} else {
 				ec = r.state.blockStore.LoadBlockCommit(prs.Height).WrappedExtendedCommit()
 			}
+			r.state.mtx.RUnlock()
 			if ec == nil {
 				continue
 			}
```
