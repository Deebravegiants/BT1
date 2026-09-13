# [?] fix(op-acceptance): eliminate race condition in super fault proof L1 head capture (#19805)

## Summary
Severity: Unknown
Chain: Optimism
Component: ethereum-optimism/optimism
Published: 2026-03-31
Source: https://github.com/ethereum-optimism/optimism/commit/c865cf8108725b158b5447aac780d3fdd0bcc0a3
Type: security-commit

## Details
fix(op-acceptance): eliminate race condition in super fault proof L1 head capture (#19805)

* fix(op-acceptance): fix flaky VariedBlockTimes by restructuring batcher choreography

The test captured L1 heads by querying the supernode's RequiredL1 values
via l1BlockWithLocalSafeBlocks, which races with continued sequencer block
production shifting those values. Instead, read the L1 head directly from
the L1 client at each stage of the batcher choreography — the invariants
(which chain's data is on L1) are maintained by which batchers are running,
not by timing windows.

Also removes the t.Skip() from all four VariedBlockTimes test variants.

Fixes ethereum-optimism/optimism#19804

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* fix(op-acceptance): apply race-free batcher choreography to all super fault proof tests

Apply the same pattern used for RunVariedBlockTimesTest to
RunSuperFaultProofTest and RunSingleChainSuperFaultProofSmokeTest.
Replace l1BlockWithLocalSafeBlocks polling with direct L1 head reads
from the L1 client, using batcher start/stop state as the
synchronization mechanism.

Remove the now-unused l1BlockWithLocalSafeBlocks helper and the "math"
import it required.

Fixes ethereum-optimism/optimism#19804

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* fix(op-acceptance): stop batchers after capturing L1 heads to prevent cleanup failure

The t.Cleanup(Batcher.Start) calls registered in Stage 1 fail with
"batcher is already running" if the batchers are still running at test
teardown. Stop them after capturing l1HeadCurrent so the cleanup can
restart them cleanly.

Fixes ethereum-optimism/optimism#19804

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* fix(op-acceptance): allow deployer options in supernode proofs presets and remove batcher cleanup

Add optionKindDeployer to supernodeProofsPresetSupportedOptionKinds so
WithL2BlockTimes (which wraps WithDeployerOptions) works with
NewSimpleInteropSupernodeProofs and NewSimpleInteropIsthmusSuper. The
underlying runtime already processes deployer options via
cfg.DeployerOptions.

Also remove t.Cleanup(Batcher.Start) and corresponding Batcher.Stop()
calls — tests don't share devnets so there's no need to restore batcher
state at teardown.

Fixes ethereum-optimism/optimism#19804

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* fix(op-acceptance): fix interop fault proof tests by using LocalSafe heads

The interop VariedBlockTimes tests were failing for two reasons:

1. EL safe label waits deadlocked: EL safe only advances after interop
   validation, which requires ALL chains to have batch data. When only one
   chain's batcher is running, EL safe never advances. Switch to waiting
   on CL LocalSafe which advances independently per-chain.

2. endTimestamp computed from cross-safe heads: nextTimestampAfterSafeHeads
   used SafeL2 (cross-safe) which lags far behind LocalSafe in interop mode.
   This caused endTimestamp to target blocks whose batch data was already on
   L1, breaking the l1HeadBefore/l1HeadAfterFirst invariants. Now uses
   LocalSafeL2 when available.

Also stops both batchers simultaneously to prevent one from submitting data
past the safe heads while waiting for the other to stall. Wires BatcherOptions
through to the two-L2 supernode runtime and adds WithBatcherStopped() preset
option.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* chore: remove unused WithBatcherStopped option

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* fix: re-add optionKindBatcher to supernode proofs preset

The BatcherOptions wiring is now supported via
multichain_supernode_runtime.go, so the preset should accept batcher
options.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

---------

Co-authored-by: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

### op-acceptance-tests/tests/interop/proofs/serial/interop_fault_proofs_test.go
```diff
@@ -26,8 +26,6 @@ func TestInteropFaultProofs_ConsolidateValidCrossChainMessage(gt *testing.T) {
 
 func TestInteropFaultProofs_VariedBlockTimes(gt *testing.T) {
 	t := devtest.SerialT(gt)
-	// TODO(#19010): Unskip once varied block time fault proofs are stable.
-	t.Skip("Skipping flaky varied block time fault proof test")
 	sys := presets.NewSimpleInteropSupernodeProofs(
 		t,
 		presets.WithChallengerCannonKonaEnabled(),
@@ -41,8 +39,6 @@ func TestInteropFaultProofs_VariedBlockTimes(gt *testing.T) {
 
 func TestInteropFaultProofs_VariedBlockTimes_FasterChainB(gt *testing.T) {
 	t := devtest.SerialT(gt)
-	// TODO(#19010): Unskip once varied block time fault proofs are stable.
-	t.Skip("Skipping flaky varied block time fault proof test")
 	sys := presets.NewSimpleInteropSupernodeProofs(
 		t,
 		presets.WithChallengerCannonKonaEnabled(),
```

### op-acceptance-tests/tests/isthmus/preinterop/interop_fault_proofs_test.go
```diff
@@ -30,8 +30,6 @@ func TestPreinteropFaultProofs_UnsafeProposal(gt *testing.T) {
 
 func TestPreinteropFaultProofs_VariedBlockTimes(gt *testing.T) {
 	t := devtest.SerialT(gt)
-	// TODO(#19010): Unskip once varied block time fault proofs are stable.
-	t.Skip("Skipping flaky varied block time fault proof test")
 	sys := presets.NewSimpleInteropIsthmusSuper(
 		t,
 		presets.WithChallengerCannonKonaEnabled(),
@@ -45,8 +43,6 @@ func TestPreinteropFaultProofs_VariedBlockTimes(gt *testing.T) {
 
 func TestPreinteropFaultProofs_VariedBlockTimes_FasterChainB(gt *testing.T) {
 	t := devtest.SerialT(gt)
-	// TODO(#19010): Unskip once varied block time fault proofs are stable.
-	t.Skip("Skipping flaky varied block time fault proof test")
 	sys := presets.NewSimpleInteropIsthmusSuper(
 		t,
 		presets.WithChallengerCannonKonaEnabled(),
```

### op-acceptance-tests/tests/superfaultproofs/singlechain.go
```diff
@@ -34,7 +34,6 @@ func RunSingleChainSuperFaultProofSmokeTest(t devtest.T, sys *presets.SingleChai
 
 	// Stop batch submission so safe head stalls, then we have a known boundary.
 	c.Batcher.Stop()
-	t.Cleanup(c.Batcher.Start)
 	sys.L2CLA.WaitForStall(types.CrossSafe)
 
 	endTimestamp := nextTimestampAfterSafeHeads(t, chains)
@@ -45,14 +44,14 @@ func RunSingleChainSuperFaultProofSmokeTest(t devtest.T, sys *presets.SingleChai
 	t.Require().NoError(err)
 	c.EL.Reached(eth.Unsafe, target, 60)
 
-	// L1 head where chain has no batch data at endTimestamp.
-	l1HeadBefore := l1BlockWithLocalSafeBlocks(t, sys.L1EL, sys.SuperRoots, endTimestamp, nil, []eth.ChainID{c.ID})
+	// Batcher is stopped, so no batch data for endTimestamp is on L1.
+	l1HeadBefore := sys.L1EL.BlockRefByLabel(eth.Unsafe).ID()
 
-	// Resume batching so the chain's data at endTimestamp becomes available.
+	// Resume batching and wait for the safe head to reach the target.
 	c.Batcher.Start()
 	sys.SuperRoots.AwaitValidatedTimestamp(endTimestamp)
-	l1HeadCurrent := latestRequiredL1(sys.SuperRoots.SuperRootAtTimestamp(endTimestamp))
-	c.Batcher.Stop()
+	c.EL.Reached(eth.Safe, target, 60)
+	l1HeadCurrent := sys.L1EL.BlockRefByLabel(eth.Unsafe).ID()
 
 	// Build expected transition states for a single chain.
 	start := superRootAtTimestamp(t, chains, startTimestamp)
```

### op-acceptance-tests/tests/superfaultproofs/superfaultproofs.go
```diff
@@ -2,7 +2,6 @@ package superfaultproofs
 
 import (
 	"context"
-	"math"
 	"math/big"
 	"math/rand"
 	"os"
@@ -73,7 +72,15 @@ func nextTimestampAfterSafeHeads(t devtest.T, chains []*chain) uint64 {
 	for _, c := range chains {
 		status, err := c.Rollup.SyncStatus(t.Ctx())
 		t.Require().NoError(err)
-		next := c.Cfg.TimestampForBlock(status.SafeL2.Number + 1)
+		// Use LocalSafeL2 when available, as it reflects the latest L1-derived
+		// head before interop cross-validation. SafeL2 (cross-safe) may lag far
+		// behind, causing endTimestamp to target blocks whose batch data is
+		// already on L1.
+		safeNum := status.SafeL2.Number
+		if status.LocalSafeL2.Number > safeNum {
+			safeNum = status.LocalSafeL2.Number
+		}
+		next := c.Cfg.TimestampForBlock(safeNum + 1)
 		if next > ts {
 			ts = next
 		}
@@ -125,39 +132,6 @@ func latestRequiredL1(resp eth.SuperRootAtTimestampResponse) eth.BlockID {
 	return latest
 }
 
-// l1BlockWithLocalSafeBlocks finds an L1 block where the specified chains either do or do not have safe blocks.
-func l1BlockWithLocalSafeBlocks(t devtest.T, l1El *dsl.L1ELNode, sn *dsl.Supernode, timestamp uint64, hasSafe, notSafe []eth.ChainID) eth.BlockID {
-	t.Logf("Finding L1 block where %v have safe blocks and %v do not", hasSafe, notSafe)
-	var l1Block eth.BlockID
-	t.Require().Eventually(func() bool {
-		resp := sn.SuperRootAtTimestamp(timestamp)
-
-		candidate := uint64(math.MaxUint64)
-		for _, id := range notSafe {
-			if optimistic, has := resp.OptimisticAtTimestamp[id]; has && optimistic.RequiredL1.Number <= candidate {
-				candidate = optimistic.RequiredL1.Number - 1 // We need this chain to not have a safe block, so L1 head must be the block before it.
-			}
-		}
-		// If we didn't have any notSafe chains, we can use the current L1 block.
-		if candidate == math.MaxUint64 {
-			candidate = resp.CurrentL1.Number
-		}
-
-		// Now verify that all the required chains have a safe block at the candidate L1 block.
-		for _, id := range hasSafe {
-			if optimistic, has := resp.OptimisticAtTimestamp[id]; !has {
-				return false
-			} else if optimistic.RequiredL1.Number > candidate {
-				return false
-			}
-		}
-
-		l1Block = l1El.BlockRefByNumber(candidate).ID()
-		return true
-	}, 2*time.Minute, 2*time.Second, "timed out waiting for l1 block")
-	return l1Block
-}
-
 // runKonaInteropProgram runs the kona interop fault proof program and checks the result.
 func runKonaInteropProgram(t devtest.T, cfg vm.Config, l1Head common.Hash, agreedPreState []byte, l2Claim common.Hash, claimTimestamp uint64, expectValid bool) {
 	tmpDir := t.TempDir()
@@ -569,39 +543,44 @@ func RunSuperFaultProofTest(t devtest.T, sys *presets.SimpleInterop) {
 	t.Require().Len(chains, 2, "expected exactly 2 interop chains")
 
 	// -- Stage 1: Freeze batch submission ----------------------------------
-	chains[1].Batcher.Stop() // Stop chain 1 first and wait for chains[0] to have at least that local safe head.
-	t.Cleanup(chains[1].Batcher.Start)
-	// Wait for safe heads to stall (local safe will continue on chains[0] but interop validation can't progress because chains[1] local safe has stalled)
-	chains[1].CLNode.WaitForStall(types.CrossSafe)
+	// Stop both batchers simultaneously, then wait for local-safe to stall on
+	// both chains. This ensures neither batcher submits data past the safe heads.
 	chains[0].Batcher.Stop()
-	t.Cleanup(chains[0].Batcher.Start)
-	chains[0].CLNode.WaitForStall(types.LocalSafe) // Wait for chains[0] local safe head to stall
+	chains[1].Batcher.Stop()
+	chains[0].CLNode.WaitForStall(types.LocalSafe)
+	chains[1].CLNode.WaitForStall(types.LocalSafe)
 
 	endTimestamp := nextTimestampAfterSafeHeads(t, chains)
 	startTimestamp := endTimestamp - 1
 
-	// Ensure both chains have produced the target blocks as unsafe.
-	for _, c := range chains {
-		target, err := c.Cfg.TargetBlockNumber(endTimestamp)
-		t.Require().NoError(err)
-		c.EL.Reached(eth.Unsafe, target, 60)
-	}
-
-	// -- Stage 2: Capture L1 heads at different batch-availability points --
+	// Wait for both chains to produce the target blocks as unsafe.
+	// Sequencers keep running freely — the L1 head invariants are maintained
+	// by which batchers are running, not by stopping sequencers.
+	target0, err := chains[0].Cfg.TargetBlockNumber(endTimestamp)
+	t.Require().NoError(err)
+	target1, err := chains[1].Cfg.TargetBlockNumber(endTimestamp)
+	t.Require().NoError(err)
+	chains[0].EL.Reached(eth.Unsafe, target0, 60)
+	chains[1].EL.Reached(eth.Unsafe, target1, 60)
 
-	// L1 head where neither chain has batch data at endTimestamp.
-	l1HeadBefore := l1BlockWithLocalSafeBlocks(t, sys.L1EL, sys.SuperRoots, endTimestamp, nil, []eth.ChainID{chains[0].ID, chains[1].ID})
+	// -- Stage 2: Capture L1 heads via batcher choreography ----------------
+	// Batchers are stopped, so no batch data for endTimestamp is on L1.
+	l1HeadBefore := sys.L1EL.BlockRefByLabel(eth.Unsafe).ID()
 
-	// L1 head where only the first chain has batch data.
+	// Start chain[0]'s batcher and wait for its local-safe head to reach the target.
+	// Chain[1]'s batcher is still stopped, so only chain[0]'s data lands on L1.
+	// We wait on the CL local-safe label because the EL safe label only advances
+	// after interop validation, which requires all chains to have batch data.
 	chains[0].Batcher.Start()
-	l1HeadAfterFirst := l1BlockWithLocalSafeBlocks(t, sys.L1EL, sys.SuperRoots, endTimestamp, []eth.ChainID{chains[0].ID}, []eth.ChainID{chains[1].ID})
-	chains[0].Batcher.Stop()
+	chains[0].CLNode.Reached(types.LocalSafe, target0, 60)
+	l1HeadAfterFirst := sys.L1EL.BlockRefByLabel(eth.Unsafe).ID()
 
-	// L1 head where both chains have batch data (fully validated).
+	// Start chain[1]'s batcher and wait for the supernode to validate, then
+	// wait for chain[1]'s safe head to reach its target.
 	chains[1].Batcher.Start()
 	sys.SuperRoots.AwaitValidatedTimestamp(endTimestamp)
-	l1HeadCurrent := latestRequiredL1(sys.SuperRoots.SuperRootAtTimestamp(endTimestamp))
-	chains[1].Batcher.Stop()
+	chains[1].CLNode.Reached(types.LocalSafe, target1, 60)
+	l1HeadCurrent := sys.L1EL.BlockRefByLabel(eth.Unsafe).ID()
 
 	// --- Stage 3: Build expected transition states --------------------------
 	start := superRootAtTimestamp(t, chains, startTimestamp)
@@ -651,36 +630,45 @@ func RunVariedBlockTimesTest(t devtest.T, sys *presets.SimpleInterop) {
 	t.Require().NotEqual(chains[0].Cfg.BlockTime, chains[1].Cfg.BlockTime,
 		"this test requires chains with different block times")
 
-	// -- Stage 1: Freeze batch submission ----------------------------------
-	chains[1].Batcher.Stop()
-	t.Cleanup(chains[1].Batcher.Start)
-	chains[1].CLNode.WaitForStall(types.CrossSafe)
+	// -- Stage 1: Setup — both batchers stopped -----------------------------
+	// Stop both batchers simultaneously, then wait for local-safe to stall on
+	// both chains. This ensures neither batcher submits data past the safe heads.
 	chains[0].Batcher.Stop()
-	t.Cleanup(chains[0].Batcher.Start)
+	chains[1].Batcher.Stop()
 	chains[0].CLNode.WaitForStall(types.LocalSafe)
+	chains[1].CLNode.WaitForStall(types.LocalSafe)
 
 	endTimestamp := nextTimestampAfterSafeHeads(t, chains)
 	startTimestamp := endTimestamp - 1
 
-	// Ensure both chains have produced the target blocks as unsafe.
-	for _, c := range chains {
-		target, err := c.Cfg.TargetBlockNumber(endTimestamp)
-		t.Require().NoError(err)
-		c.EL.Reached(eth.Unsafe, target, 60)
-	}
-
-	// -- Stage 2: Capture L1 heads at different batch-availability points --
+	// Wait for both chains to produce the target blocks as unsafe.
+	// Sequencers keep running freely — the L1 head invariants are maintained
+	// by which batchers are running, not by stopping sequencers.
+	target0, err := chains[0].Cfg.TargetBlockNumber(endTimestamp)
+	t.Require().NoError(err)
+	target1, err := chains[1].Cfg.TargetBlockNumber(endTimestamp)
+	t.Require().NoError(err)
+	chains[0].EL.Reached(eth.Unsafe, target0, 60)
+	chains[1].EL.Reached(eth.Unsafe, target1, 60)
 
-	l1HeadBefore := l1BlockWithLocalSafeBlocks(t, sys.L1EL, sys.SuperRoots, endTimestamp, nil, []eth.ChainID{chains[0].ID, chains[1].ID})
+	// -- Stage 2: Capture L1 heads via batcher choreography ----------------
+	// Batchers are stopped, so no batch data for endTimestamp is on L1.
+	l1HeadBefore := sys.L1EL.BlockRefByLabel(eth.Unsafe).ID()
 
+	// Start chain[0]'s batcher and wait for its local-safe head to reach the target.
+	// Chain[1]'s batcher is still stopped, so only chain[0]'s data lands on L1.
+	// We wait on the CL local-safe label because the EL safe label only advances
+	// after interop validation, which requires all chains to have batch data.
 	chains[0].Batcher.Start()
-	l1HeadAfterFirst := l1BlockWithLocalSafeBlocks(t, sys.L1EL, sys.SuperRoots, endTimestamp, []eth.ChainID{chains[0].ID}, []eth.ChainID{chains[1].ID})
-	chains[0].Batcher.Stop()
+	chains[0].CLNode.Reached(types.LocalSafe, target0, 60)
+	l1HeadAfterFirst := sys.L1EL.BlockRefByLabel(eth.Unsafe).ID()
 
+	// Start chain[1]'s batcher and wait for the supernode to validate, then
+	// wait for chain[1]'s safe head to reach its target.
 	chains[1].Batcher.Start()
 	sys.SuperRoots.AwaitValidatedTimestamp(endTimestamp)
-	l1HeadCurrent := latestRequiredL1(sys.SuperRoots.SuperRootAtTimestamp(endTimestamp))
-	chains[1].Batcher.Stop()
+	chains[1].CLNode.Reached(types.LocalSafe, target1, 60)
+	l1HeadCurrent := sys.L1EL.BlockRefByLabel(eth.Unsafe).ID()
 
 	// -- Stage 3: Build expected transition states --------------------------
 	start := superRootAtTimestamp(t, chains, startTimestamp)
```

### op-devstack/presets/option_validation.go
```diff
@@ -147,7 +147,9 @@ const simpleInteropSuperProofsPresetSupportedOptionKinds = optionKindDeployer |
 	optionKindMaxSequencingWindow |
 	optionKindRequireInteropNotAtGen
 
-const supernodeProofsPresetSupportedOptionKinds = optionKindChallengerCannonKona |
+const supernodeProofsPresetSupportedOptionKinds = optionKindDeployer |
+	optionKindBatcher |
+	optionKindChallengerCannonKona |
 	optionKindL1EL
 
 const twoL2SupernodePresetSupportedOptionKinds = optionKindDeployer |
```

### op-devstack/sysgo/multichain_supernode_runtime.go
```diff
@@ -204,9 +204,9 @@ func newTwoL2SupernodeRuntimeWithConfig(t devtest.T, enableInterop bool, delaySe
 		jwtSecret,
 	)
 
-	l2ABatcher := startMinimalBatcher(t, keys, l2ANet, l1EL, l2ACL, l2AEL)
+	l2ABatcher := startMinimalBatcher(t, keys, l2ANet, l1EL, l2ACL, l2AEL, cfg.BatcherOptions...)
 	l2AProposer := startMinimalProposer(t, keys, l2ANet, l1EL, l2ACL)
-	l2BBatcher := startMinimalBatcher(t, keys, l2BNet, l1EL, l2BCL, l2BEL)
+	l2BBatcher := startMinimalBatcher(t, keys, l2BNet, l1EL, l2BCL, l2BEL, cfg.BatcherOptions...)
 	l2BProposer := startMinimalProposer(t, keys, l2BNet, l1EL, l2BCL)
 
 	faucetService := startFaucetsForRPCs(t, keys, map[eth.ChainID]string{
```
