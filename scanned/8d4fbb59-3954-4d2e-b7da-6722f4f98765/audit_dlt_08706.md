# [?] fix: resolve race condition in storage test goroutines (#3509)

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/nitro
Published: 2025-08-19
Source: https://github.com/OffchainLabs/nitro/commit/e6d71a363af9ae6130621b189860f8d2b60ca6ec
Type: security-commit

## Details
fix: resolve race condition in storage test goroutines (#3509)

Co-authored-by: Pepper Lebeck-Jobe <pepper@offchainlabs.com>

## Patch
### arbos/storage/storage_test.go
```diff
@@ -116,14 +116,14 @@ func TestOpenCachedSubStorage(t *testing.T) {
 		j := i % len(subSpaceIDs)
 		subSpaceID, expectedKey := subSpaceIDs[j], expectedKeys[j]
 		wg.Add(1)
-		go func() {
+		go func(subSpaceID []byte, expectedKey []byte) {
 			defer wg.Done()
 			<-start
 			ss := s.OpenCachedSubStorage(subSpaceID)
 			if !bytes.Equal(ss.storageKey, expectedKey) {
 				errs <- fmt.Errorf("unexpected storage key, want: %v, have: %v", expectedKey, ss.storageKey)
 			}
-		}()
+		}(subSpaceID, expectedKey)
 	}
 	close(start)
 	wg.Wait()
@@ -152,14 +152,14 @@ func TestMapAddressCache(t *testing.T) {
 		j := i % len(keys)
 		key, expected := keys[j], expectedMapped[j]
 		wg.Add(1)
-		go func() {
+		go func(key common.Hash, expected common.Hash) {
 			defer wg.Done()
 			<-start
 			mapped := s.mapAddress(key)
 			if !bytes.Equal(mapped.Bytes(), expected.Bytes()) {
 				errs <- fmt.Errorf("unexpected storage key, want: %v, have: %v", expected, mapped)
 			}
-		}()
+		}(key, expected)
 	}
 	close(start)
 	wg.Wait()
```
