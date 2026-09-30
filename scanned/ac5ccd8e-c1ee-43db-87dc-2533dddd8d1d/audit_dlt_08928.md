# [?] Fix guardian set initialization race condition (#191)

## Summary
Severity: Unknown
Chain: Wormhole
Component: wormhole-foundation/wormhole
Published: 2021-03-23
Source: https://github.com/wormhole-foundation/wormhole/commit/f5560eb3ff59e809f087a6722420b266ffd1620d
Type: security-commit

## Details
Fix guardian set initialization race condition (#191)

Fixes #184

## Patch
### bridge/pkg/processor/observation.go
```diff
@@ -129,6 +129,17 @@ func (p *Processor) handleObservation(ctx context.Context, m *gossipv1.SignedObs
 		gs = p.gs
 	}
 
+	// We haven't yet observed the trusted guardian set on Ethereum, and therefore, it's impossible to verify it.
+	// May as well not have received it/been offline - drop it and wait for the guardian set.
+	if gs == nil {
+		p.logger.Warn("dropping observations since we haven't initialized our guardian set yet",
+			zap.String("digest", their_addr.Hex()),
+			zap.String("their_addr", their_addr.Hex()),
+		)
+		observationsFailedTotal.WithLabelValues("uninitialized_guardian_set").Inc()
+		return
+	}
+
 	// Verify that m.Addr is included in the guardian set. If it's not, drop the message. In case it's us
 	// who have the outdated guardian set, we'll just wait for the message to be retransmitted eventually.
 	_, ok := gs.KeyIndex(their_addr)
```
