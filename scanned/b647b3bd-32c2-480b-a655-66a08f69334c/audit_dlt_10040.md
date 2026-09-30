# [?] fixed race condition in test

## Summary
Severity: Unknown
Chain: MultiversX
Component: multiversx/mx-chain-go
Published: 2026-06-29
Source: https://github.com/multiversx/mx-chain-go/commit/88468114175a882eea3ed32b8a7ce89853db9e99
Type: security-commit

## Details
fixed race condition in test

## Patch
### consensus/spos/bls/v2/subroundSignature.go
```diff
@@ -278,19 +278,22 @@ func (sr *subroundSignature) doSignatureJobForManagedKeys(ctx context.Context) b
 		select {
 		case <-sigCtx.Done():
 			log.Debug("doSignatureJobForManagedKeys: timeout while sending signatures")
+			wg.Wait()
 			return false
 		default:
 		}
 
 		err := checkGoRoutinesThrottler(sigCtx, sr.signatureThrottler)
 		if err != nil {
 			log.Debug("doSignatureJobForManagedKeys.checkGoRoutinesThrottler", "err", err)
+			wg.Wait()
 			return false
 		}
 		sr.signatureThrottler.StartProcessing()
 		wg.Add(1)
 
 		go func(sigCtx context.Context, idx int, pk string) {
+			defer wg.Done()
 			defer sr.signatureThrottler.EndProcessing()
 
 			signatureSent := sr.sendSignatureForManagedKey(sigCtx, idx, pk)
@@ -299,7 +302,6 @@ func (sr *subroundSignature) doSignatureJobForManagedKeys(ctx context.Context) b
 			} else {
 				sentSigForAllKeys.SetValue(false)
 			}
-			wg.Done()
 		}(sigCtx, idx, pk)
 	}
 
```

### consensus/spos/bls/v2/subroundSignature_test.go
```diff
@@ -1050,7 +1050,11 @@ func TestSubroundSignature_DoSignatureJobForManagedKeys(t *testing.T) {
 		}
 		assert.Equal(t, 3, numFinishedJobs)
 
-		assert.Equal(t, 3, len(signaturesBroadcast))
+		mutex.Lock()
+		numSignaturesBroadcast := len(signaturesBroadcast)
+		mutex.Unlock()
+
+		assert.Equal(t, 3, numSignaturesBroadcast)
 	})
 
 	t.Run("context done should return early", func(t *testing.T) {
```
