# [?] Fix infinite stack overflow if caching is disabled (#11669)

## Summary
Severity: Unknown
Chain: Bridge
Component: smartcontractkit/ccip
Published: 2024-01-02
Source: https://github.com/smartcontractkit/ccip/commit/6b740c57bb9adcedac883491d47f723a1f029183
Type: security-commit

## Details
Fix infinite stack overflow if caching is disabled (#11669)

## Patch
### core/services/relay/evm/mercury/wsrpc/cache/cache_set.go
```diff
@@ -67,7 +67,7 @@ func (cs *cacheSet) Close() error {
 func (cs *cacheSet) Get(ctx context.Context, client Client) (f Fetcher, err error) {
 	if cs.cfg.LatestReportTTL == 0 {
 		// caching disabled
-		return client, nil
+		return nil, nil
 	}
 	ok := cs.IfStarted(func() {
 		f, err = cs.get(ctx, client)
```

### core/services/relay/evm/mercury/wsrpc/cache/cache_set_test.go
```diff
@@ -23,13 +23,13 @@ func Test_CacheSet(t *testing.T) {
 
 		var err error
 		var f Fetcher
-		t.Run("with caching disabled, returns the passed client", func(t *testing.T) {
+		t.Run("with caching disabled, returns nil, nil", func(t *testing.T) {
 			assert.Len(t, disabledCs.caches, 0)
 
 			f, err = disabledCs.Get(ctx, c)
 			require.NoError(t, err)
 
-			assert.Same(t, c, f)
+			assert.Nil(t, f)
 			assert.Len(t, disabledCs.caches, 0)
 		})
 
```

### core/services/relay/evm/mercury/wsrpc/client_test.go
```diff
@@ -17,6 +17,14 @@ import (
 	"github.com/smartcontractkit/chainlink/v2/core/services/relay/evm/mercury/wsrpc/pb"
 )
 
+// simulate start without dialling
+func simulateStart(ctx context.Context, t *testing.T, c *client) {
+	require.NoError(t, c.StartOnce("Mock WSRPC Client", func() (err error) {
+		c.cache, err = c.cacheSet.Get(ctx, c)
+		return err
+	}))
+}
+
 var _ cache.CacheSet = &mockCacheSet{}
 
 type mockCacheSet struct{}
@@ -160,9 +168,8 @@ func Test_Client_LatestReport(t *testing.T) {
 		c.conn = conn
 		c.rawClient = wsrpcClient
 
-		// simulate start without dialling
-		require.NoError(t, c.StartOnce("Mock WSRPC Client", func() error { return nil }))
 		servicetest.Run(t, cacheSet)
+		simulateStart(ctx, t, c)
 
 		for i := 0; i < 5; i++ {
 			r, err := c.LatestReport(ctx, req)
@@ -195,12 +202,8 @@ func Test_Client_LatestReport(t *testing.T) {
 		c.conn = conn
 		c.rawClient = wsrpcClient
 
-		// simulate start without dialling
-		require.NoError(t, c.StartOnce("Mock WSRPC Client", func() error { return nil }))
-		var err error
 		servicetest.Run(t, cacheSet)
-		c.cache, err = cacheSet.Get(ctx, c)
-		require.NoError(t, err)
+		simulateStart(ctx, t, c)
 
 		for i := 0; i < 5; i++ {
 			r, err := c.LatestReport(ctx, req)
```
