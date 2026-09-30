# [?] fix more nil pointer dereferences

## Summary
Severity: Unknown
Chain: Rollkit
Component: evstack/ev-node
Published: 2023-11-19
Source: https://github.com/evstack/ev-node/commit/1d4b54268f0ef3892ce400a5dcac629cd26b5bb0
Type: security-commit

## Details
fix more nil pointer dereferences

## Patch
### state/executor.go
```diff
@@ -111,11 +111,12 @@ func (e *BlockExecutor) CreateBlock(ctx context.Context, height uint64, lastComm
 				},
 				//LastHeaderHash: lastHeaderHash,
 				//LastCommitHash:  lastCommitHash,
-				DataHash:        make(types.Hash, 32),
-				ConsensusHash:   make(types.Hash, 32),
-				AppHash:         state.AppHash,
-				LastResultsHash: state.LastResultsHash,
-				ProposerAddress: e.proposerAddress,
+				DataHash:            make(types.Hash, 32),
+				ConsensusHash:       make(types.Hash, 32),
+				AppHash:             state.AppHash,
+				LastResultsHash:     state.LastResultsHash,
+				ProposerAddress:     e.proposerAddress,
+				NextAggregatorsHash: state.NextValidators.Hash(),
 			},
 			Commit: *lastCommit,
 		},
@@ -173,11 +174,14 @@ func (e *BlockExecutor) ProcessProposal(
 	state types.State,
 ) (bool, error) {
 	resp, err := e.proxyApp.ProcessProposal(context.TODO(), &abci.RequestProcessProposal{
-		Hash:               block.Hash(),
-		Height:             int64(block.Height()),
-		Time:               block.Time(),
-		Txs:                block.Data.Txs.ToSliceOfBytes(),
-		ProposedLastCommit: abci.CommitInfo{},
+		Hash:   block.Hash(),
+		Height: int64(block.Height()),
+		Time:   block.Time(),
+		Txs:    block.Data.Txs.ToSliceOfBytes(),
+		ProposedLastCommit: abci.CommitInfo{
+			Round: 0,
+			Votes: []abci.VoteInfo{},
+		},
 		Misbehavior:        []abci.Misbehavior{},
 		ProposerAddress:    e.proposerAddress,
 		NextValidatorsHash: block.SignedHeader.NextAggregatorsHash,
```
