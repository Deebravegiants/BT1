# [?] fix(common): fixes deadlock in OCI FragmentedUploadObject and FragmentedDownloadObject (#2221)

## Summary
Severity: Unknown
Chain: EigenDA
Component: Layr-Labs/eigenda
Published: 2025-10-27
Source: https://github.com/Layr-Labs/eigenda/commit/3f150a95c0340f3bd1afbabf30538a7f399bbbd6
Type: security-commit

## Details
fix(common): fixes deadlock in OCI FragmentedUploadObject and FragmentedDownloadObject (#2221)

* Fix goroutine deadlock in OCI FragmentedUploadObject and FragmentedDownloadObject

The OCI client was using a semaphore pattern with a pre-filled channel but had the channel operations backwards, causing deadlock.

- The concurrency limiter is initialized as a semaphore with workers tokens pre-filled in the channel. However, the
code was trying to send to acquire a token (c.concurrencyLimiter <- struct{}{}) and receive to release a token
(<-c.concurrencyLimiter). Since the channel starts full, sending to it blocks indefinitely.
- The fix swaps the channel operations to match the semaphore pattern:
    - Acquire token: <-c.concurrencyLimiter (receive from channel)
    - Release token: c.concurrencyLimiter <- struct{}{} (send to channel)

* update unit test

* Lint

## Patch
### common/oci/object_storage.go
```diff
@@ -256,10 +256,10 @@ func (c *ociClient) FragmentedUploadObject(
 
 	for _, fragment := range fragments {
 		fragmentCapture := fragment
-		c.concurrencyLimiter <- struct{}{}
+		<-c.concurrencyLimiter
 		go func() {
 			defer func() {
-				<-c.concurrencyLimiter
+				c.concurrencyLimiter <- struct{}{}
 			}()
 			c.fragmentedWriteTask(ctx, resultChannel, fragmentCapture, bucket)
 		}()
@@ -320,10 +320,10 @@ func (c *ociClient) FragmentedDownloadObject(
 	for i, fragmentKey := range fragmentKeys {
 		boundFragmentKey := fragmentKey
 		boundI := i
-		c.concurrencyLimiter <- struct{}{}
+		<-c.concurrencyLimiter
 		go func() {
 			defer func() {
-				<-c.concurrencyLimiter
+				c.concurrencyLimiter <- struct{}{}
 			}()
 			c.readTask(ctx, resultChannel, bucket, boundFragmentKey, boundI)
 		}()
```

### common/oci/object_storage_test.go
```diff
@@ -1415,3 +1415,57 @@ func TestObjectStorageConfig_WorkerCalculations(t *testing.T) {
 		})
 	}
 }
+
+// This test verifies the worker semaphore pattern does not deadlock
+func TestOCIClient_ConcurrencyLimiter(t *testing.T) {
+	t.Run("Semaphore pattern works with correct token operations", func(t *testing.T) {
+		limiter := make(chan struct{}, 2)
+
+		// Pre-fill with tokens (semaphore pattern)
+		limiter <- struct{}{}
+		limiter <- struct{}{}
+
+		// Test that we can acquire tokens (receive operation)
+		<-limiter // Should not block
+		<-limiter // Should not block
+
+		// Channel should now be empty, so sending should work (release operation)
+		limiter <- struct{}{} // Should not block
+		limiter <- struct{}{} // Should not block
+
+		// Verify channel is full again
+		assert.Equal(t, 2, len(limiter))
+	})
+
+	t.Run("Check concurrency limiter initialization", func(t *testing.T) {
+		// We can't easily test the actual fragmented methods due to OCI SDK dependencies,
+		// but we can test the concurrency limiter initialization and basic pattern
+
+		cfg := ObjectStorageConfig{
+			FragmentParallelismConstant: 3,
+		}
+
+		// Test client creation logic - will fail at OCI auth (expected)
+		_, err := NewObjectStorageClient(context.Background(), cfg, &mockLogger{})
+		assert.Error(t, err) // Expected due to missing OCI credentials
+		assert.Contains(t, err.Error(), "failed to create OCI Object Storage client")
+	})
+
+	t.Run("Fragment count calculation checks", func(t *testing.T) {
+		assert.Equal(t, 1, GetFragmentCount(5, 10))  // Small data
+		assert.Equal(t, 3, GetFragmentCount(25, 10)) // 25 bytes with 10-byte fragments = 3 fragments
+		assert.Equal(t, 4, GetFragmentCount(35, 10)) // 35 bytes with 10-byte fragments = 4 fragments
+	})
+
+	t.Run("Validate fragment recombination ordering", func(t *testing.T) {
+		fragments := []*s3.Fragment{
+			{FragmentKey: "test-1", Data: []byte("bcdefghijk"), Index: 1},
+			{FragmentKey: "test-0", Data: []byte("0123456789"), Index: 0},
+			{FragmentKey: "test-2f", Data: []byte("lmnop"), Index: 2}, // Final fragment
+		}
+
+		result, err := RecombineFragments(fragments)
+		assert.NoError(t, err)
+		assert.Equal(t, []byte("0123456789bcdefghijklmnop"), result)
+	})
+}
```
