# [?] cre-3245: prevent panic on empty observation while tearing down (#21878)

## Summary
Severity: Unknown
Chain: Chainlink
Component: smartcontractkit/chainlink
Published: 2026-04-07
Source: https://github.com/smartcontractkit/chainlink/commit/a7be9295dd9a8ef457fffaa012f0ab4cb6dc3486
Type: security-commit

## Details
cre-3245: prevent panic on empty observation while tearing down (#21878)

## Patch
### core/services/ring/plugin.go
```diff
@@ -172,6 +172,9 @@ func (p *Plugin) getHealthyShards(shardHealth map[uint32]int) []uint32 {
 }
 
 func (p *Plugin) Outcome(_ context.Context, outctx ocr3types.OutcomeContext, _ types.Query, aos []types.AttributedObservation) (ocr3types.Outcome, error) {
+	if len(aos) == 0 {
+		return nil, errors.New("RingOCR Outcome: no attributed observations")
+	}
 	currentShardHealth, allWorkflows, nows, wantShardVotes := p.collectShardInfo(aos)
 	p.lggr.Infow("RingOCR Outcome collect shard info", "currentShardHealth", currentShardHealth, "wantShardVotes", wantShardVotes)
 
```
