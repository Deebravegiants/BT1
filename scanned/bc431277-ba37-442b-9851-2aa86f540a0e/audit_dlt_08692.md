# [?] fix nil dereference

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/nitro
Published: 2026-03-25
Source: https://github.com/OffchainLabs/nitro/commit/b68bd9c820030054e3d31589f741be115dbca00e
Type: security-commit

## Details
fix nil dereference

Signed-off-by: Igor Braga <5835477+bragaigor@users.noreply.github.com>

## Patch
### system_tests/common_test.go
```diff
@@ -1065,7 +1065,7 @@ func (b *NodeBuilder) BuildL2(t *testing.T) func() {
 		t, b.L2Info, b.dataDir, b.chainConfig, b.arbOSInit, nil, b.l2StackConfig, b.execConfig, b.TrieNoAsyncFlush)
 
 	execConfigFetcher := NewCommonConfigFetcher(b.execConfig)
-	execNode, err := gethexec.CreateExecutionNode(b.ctx, b.L2.Stack, executionDB, blockchain, nil, execConfigFetcher, 0, b.L2.ExecNode.ParentChain)
+	execNode, err := gethexec.CreateExecutionNode(b.ctx, b.L2.Stack, executionDB, blockchain, nil, execConfigFetcher, 0, nil)
 	Require(t, err)
 	b.L2.ExecutionConfigFetcher = execConfigFetcher
 
```
