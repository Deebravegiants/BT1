# [?] fix: add frequency check to avoid potential panic

## Summary
Severity: Unknown
Chain: Flare
Component: flare-foundation/go-flare
Published: 2026-05-28
Source: https://github.com/flare-foundation/go-flare/commit/40e97bc0416da603bab670156c8e3653594a37f0
Type: security-commit

## Details
fix: add frequency check to avoid potential panic

## Patch
### avalanchego/network/p2p/gossip/gossip.go
```diff
@@ -582,6 +582,10 @@ func (p *PushGossiper[_]) updateMetrics(nowUnixNano float64) {
 
 // Every calls [Gossip] every [frequency] amount of time.
 func Every(ctx context.Context, log logging.Logger, gossiper Gossiper, frequency time.Duration) {
+	if frequency <= 0 {
+		return
+	}
+
 	ticker := time.NewTicker(frequency)
 	defer ticker.Stop()
 
```

### avalanchego/network/p2p/gossip/gossip_test.go
```diff
@@ -232,6 +232,26 @@ func TestEvery(t *testing.T) {
 	<-ctx.Done()
 }
 
+func TestEveryWithNonPositiveFrequency(t *testing.T) {
+	for _, frequency := range []time.Duration{
+		0,
+		-time.Second,
+	} {
+		t.Run(frequency.String(), func(t *testing.T) {
+			calls := 0
+			gossiper := &TestGossiper{
+				GossipF: func(context.Context) error {
+					calls++
+					return nil
+				},
+			}
+
+			Every(t.Context(), logging.NoLog{}, gossiper, frequency)
+			require.Zero(t, calls)
+		})
+	}
+}
+
 func TestValidatorGossiper(t *testing.T) {
 	require := require.New(t)
 
```
