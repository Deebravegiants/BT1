# [?] Fix cold path cache hit panic (#11768)

## Summary
Severity: Unknown
Chain: Bridge
Component: smartcontractkit/ccip
Published: 2024-01-12
Source: https://github.com/smartcontractkit/ccip/commit/c32efca111a53c3c1129260a4501b4cd404c888b
Type: security-commit

## Details
Fix cold path cache hit panic (#11768)

This is very difficult/impossible to test since it's reliant on specific
timing.

## Patch
### core/services/relay/evm/mercury/wsrpc/cache/cache.go
```diff
@@ -237,7 +237,7 @@ func (m *memCache) LatestReport(ctx context.Context, req *pb.LatestReportRequest
 		// CACHE HIT
 		promCacheHitCount.WithLabelValues(m.client.ServerURL(), feedIDHex).Inc()
 		m.lggr.Tracew("LatestReport CACHE HIT (cold path)", "feedID", feedIDHex)
-		defer v.RUnlock()
+		defer v.Unlock()
 		return v.val, nil
 	} else if v.fetching {
 		// CACHE WAIT
```
