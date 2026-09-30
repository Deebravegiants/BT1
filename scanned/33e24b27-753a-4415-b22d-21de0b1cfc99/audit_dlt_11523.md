# [?] fix(fibre/grpc): sync.Once -> sync.Mutex to fix data race inn ClientCache (#233)

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-app
Published: 2026-03-05
Source: https://github.com/celestiaorg/celestia-app/commit/298da34852fa2d4fb800996a0aa6ad43a5cabd65
Type: security-commit

## Details
fix(fibre/grpc): sync.Once -> sync.Mutex to fix data race inn ClientCache (#233)

Close() read entry.clientCloser without holding the entry lock, racing
with GetClient's write inside sync.Once.Do. Replace Once with Mutex so
both methods synchronize on the same lock.

This was a flake on one of the recent PRs

## Patch
### fibre/internal/grpc/client_cache.go
```diff
@@ -18,7 +18,7 @@ type ClientCache struct {
 
 // clientEntry holds a lazily-initialized [Client].
 type clientEntry struct {
-	sync.Once
+	sync.Mutex
 	clientCloser Client
 	err          error
 }
@@ -44,15 +44,16 @@ func (cc *ClientCache) GetClient(ctx context.Context, val *core.Validator) (Clie
 	}
 	cc.mu.Unlock()
 
-	entry.Do(func() {
-		client, err := cc.newClient(ctx, val)
-		if err != nil {
-			entry.err = err
-			return
-		}
-		entry.clientCloser = client
-	})
+	entry.Lock()
+	defer entry.Unlock()
+	if entry.clientCloser != nil {
+		return entry.clientCloser, nil
+	}
+	if entry.err != nil {
+		return nil, entry.err
+	}
 
+	entry.clientCloser, entry.err = cc.newClient(ctx, val)
 	return entry.clientCloser, entry.err
 }
 
@@ -61,9 +62,11 @@ func (cc *ClientCache) Close() (err error) {
 	cc.mu.Lock()
 	defer cc.mu.Unlock()
 	for _, entry := range cc.clients {
+		entry.Lock()
 		if entry.clientCloser != nil {
 			err = errors.Join(err, entry.clientCloser.Close())
 		}
+		entry.Unlock()
 	}
 	cc.clients = make(map[string]*clientEntry)
 	return err
```

### fibre/internal/grpc/client_cache_test.go
```diff
@@ -71,6 +71,33 @@ func TestClientCache(t *testing.T) {
 	assert.True(t, mockClient2.closed)
 }
 
+// TestClientCacheGetCloseConcurrentRace verifies that concurrent calls to GetClient
+// and Close do not produce a data race. Run with -race to catch the regression.
+// The original sync.Once implementation allowed Close to read entry.clientCloser
+// without holding the entry lock, racing with GetClient's write inside Do.
+func TestClientCacheGetCloseConcurrentRace(t *testing.T) {
+	const numGoroutines = 50
+	cache := grpc.NewClientCache(mockClientFn(false), 1)
+	val := &core.Validator{Address: []byte("validator-1")}
+
+	var wg sync.WaitGroup
+	wg.Add(numGoroutines + 1)
+
+	for range numGoroutines {
+		go func() {
+			defer wg.Done()
+			cache.GetClient(t.Context(), val) //nolint:errcheck
+		}()
+	}
+
+	go func() {
+		defer wg.Done()
+		cache.Close() //nolint:errcheck
+	}()
+
+	wg.Wait()
+}
+
 // mockFibreClientCloser is a mock implementation for testing
 type mockFibreClientCloser struct {
 	types.FibreClient
```
