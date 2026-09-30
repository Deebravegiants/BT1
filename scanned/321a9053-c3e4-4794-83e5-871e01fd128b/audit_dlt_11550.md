# [?] Add data race protection in GetHeaderV1 and RegisterValidatorV1 (#117)

## Summary
Severity: Unknown
Chain: MEV
Component: flashbots/mev-boost
Published: 2022-05-03
Source: https://github.com/flashbots/mev-boost/commit/b5bc0bf01310783a8cb80b23b62ee880b5569e57
Type: security-commit

## Details
Add data race protection in GetHeaderV1 and RegisterValidatorV1 (#117)

* Add data race protection in RegisterValidatorV1

Signed-off-by: Luca Georges Francois <luca.georges-francois@epitech.eu>

* Add data race protection in GetHeaderV1

Signed-off-by: Luca Georges Francois <luca.georges-francois@epitech.eu>

## Patch
### server/service.go
```diff
@@ -109,8 +109,13 @@ func (m *BoostService) RegisterValidatorV1(ctx context.Context, message types.Re
 		return nil, rpcErrInvalidSignature
 	}
 
-	ok := false // at least one builder has returned true
-	var lastRelayError error
+	type safeRegisterContainer struct {
+		mu             sync.Mutex
+		ok             bool // at least one builder has returned true
+		lastRelayError error
+	}
+	container := safeRegisterContainer{}
+
 	var wg sync.WaitGroup
 	for _, url := range m.relayURLs {
 		wg.Add(1)
@@ -125,7 +130,10 @@ func (m *BoostService) RegisterValidatorV1(ctx context.Context, message types.Re
 			}
 			if res.Error != nil {
 				logMethod.WithFields(logrus.Fields{"error": res.Error, "url": url}).Warn("error reply from relay")
-				lastRelayError = res.Error
+				// We can unlock using defer because we're leaving the routine right now
+				container.mu.Lock()
+				defer container.mu.Unlock()
+				container.lastRelayError = res.Error
 				return
 			}
 
@@ -138,7 +146,9 @@ func (m *BoostService) RegisterValidatorV1(ctx context.Context, message types.Re
 			}
 
 			// Ok should be true if any one builder responds with OK
-			ok = ok || builderResult == ServiceStatusOk
+			container.mu.Lock()
+			defer container.mu.Unlock()
+			container.ok = container.ok || builderResult == ServiceStatusOk
 		}(url)
 	}
 
@@ -147,9 +157,9 @@ func (m *BoostService) RegisterValidatorV1(ctx context.Context, message types.Re
 
 	// If no relay responded true, return the last error message, or a generic error
 	var err error
-	if !ok {
-		err = lastRelayError
-		if lastRelayError == nil {
+	if !container.ok {
+		err = container.lastRelayError
+		if container.lastRelayError == nil {
 			err = errors.New("no relay responded true")
 		}
 		return nil, err
@@ -166,9 +176,16 @@ func (m *BoostService) GetHeaderV1(ctx context.Context, slot hexutil.Uint64, pub
 		return nil, rpcErrInvalidPubkey
 	}
 
+	type safeHeaderContainer struct {
+		mu             sync.Mutex
+		result         *types.GetHeaderResponse
+		lastRelayError error
+	}
+	container := safeHeaderContainer{
+		result: new(types.GetHeaderResponse),
+	}
+
 	// Call the relay
-	result := new(types.GetHeaderResponse)
-	var lastRelayError error
 	var wg sync.WaitGroup
 	for _, relayURL := range m.relayURLs {
 		wg.Add(1)
@@ -183,7 +200,10 @@ func (m *BoostService) GetHeaderV1(ctx context.Context, slot hexutil.Uint64, pub
 			}
 			if res.Error != nil {
 				logMethod.WithFields(logrus.Fields{"error": res.Error, "url": url}).Warn("error reply from relay")
-				lastRelayError = res.Error
+				// We can unlock using defer because we're leaving the routine right now
+				container.mu.Lock()
+				defer container.mu.Unlock()
+				container.lastRelayError = res.Error
 				return
 			}
 
@@ -196,17 +216,20 @@ func (m *BoostService) GetHeaderV1(ctx context.Context, slot hexutil.Uint64, pub
 			}
 
 			// Skip processing this result if lower fee than previous
-			if result.Message.Value != nil && (_result.Message.Value == nil || _result.Message.Value.ToInt().Cmp(result.Message.Value.ToInt()) < 1) {
+			container.mu.Lock()
+			defer container.mu.Unlock()
+			if container.result.Message.Value != nil && (_result.Message.Value == nil ||
+				_result.Message.Value.ToInt().Cmp(container.result.Message.Value.ToInt()) < 1) {
 				return
 			}
 
 			// Use this relay's response as mev-boost response because it's most profitable
-			result = _result
+			container.result = _result
 			logMethod.WithFields(logrus.Fields{
-				"blockNumber": result.Message.Header.BlockNumber,
-				"blockHash":   result.Message.Header.BlockHash,
-				"txRoot":      result.Message.Header.TransactionsRoot.Hex(),
-				"value":       result.Message.Value.String(),
+				"blockNumber": container.result.Message.Header.BlockNumber,
+				"blockHash":   container.result.Message.Header.BlockHash,
+				"txRoot":      container.result.Message.Header.TransactionsRoot.Hex(),
+				"value":       container.result.Message.Value.String(),
 				"url":         url,
 			}).Info("GetPayloadHeaderV1: successfully got more valuable payload header")
 		}(relayURL)
@@ -215,19 +238,19 @@ func (m *BoostService) GetHeaderV1(ctx context.Context, slot hexutil.Uint64, pub
 	// Wait for responses...
 	wg.Wait()
 
-	if result.Message.Header.BlockHash == types.NilHash {
+	if container.result.Message.Header.BlockHash == types.NilHash {
 		logMethod.WithFields(logrus.Fields{
 			"hash":           hash,
-			"lastRelayError": lastRelayError,
+			"lastRelayError": container.lastRelayError,
 		}).Error("GetPayloadHeaderV1: no successful response from relays")
 
-		if lastRelayError != nil {
-			return nil, lastRelayError
+		if container.lastRelayError != nil {
+			return nil, container.lastRelayError
 		}
 		return nil, fmt.Errorf("no valid GetHeaderV1 response from relays for hash %s", hash)
 	}
 
-	return result, nil
+	return container.result, nil
 }
 
 // GetPayloadV1 TODO
```
