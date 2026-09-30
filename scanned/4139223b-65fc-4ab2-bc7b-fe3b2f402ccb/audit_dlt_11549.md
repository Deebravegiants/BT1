# [?] Fix data race in service test (#242)

## Summary
Severity: Unknown
Chain: MEV
Component: flashbots/mev-boost
Published: 2022-08-06
Source: https://github.com/flashbots/mev-boost/commit/222be4e4ba0f94cb291ce8d90f1fc75932a69886
Type: security-commit

## Details
Fix data race in service test (#242)

Signed-off-by: Luca Georges Francois <luca.georges-francois@epitech.eu>

## Patch
### server/mock_relay.go
```diff
@@ -34,9 +34,9 @@ type mockRelay struct {
 	requestCount map[string]int
 
 	// Overriders
-	HandlerOverrideRegisterValidator func(w http.ResponseWriter, req *http.Request)
-	HandlerOverrideGetHeader         func(w http.ResponseWriter, req *http.Request)
-	HandlerOverrideGetPayload        func(w http.ResponseWriter, req *http.Request)
+	handlerOverrideRegisterValidator func(w http.ResponseWriter, req *http.Request)
+	handlerOverrideGetHeader         func(w http.ResponseWriter, req *http.Request)
+	handlerOverrideGetPayload        func(w http.ResponseWriter, req *http.Request)
 
 	// Default responses placeholders, used if overrider does not exist
 	GetHeaderResponse  *types.GetHeaderResponse
@@ -123,8 +123,10 @@ func (m *mockRelay) handleStatus(w http.ResponseWriter, req *http.Request) {
 
 // By default, handleRegisterValidator returns a default types.SignedValidatorRegistration
 func (m *mockRelay) handleRegisterValidator(w http.ResponseWriter, req *http.Request) {
-	if m.HandlerOverrideRegisterValidator != nil {
-		m.HandlerOverrideRegisterValidator(w, req)
+	m.mu.Lock()
+	defer m.mu.Unlock()
+	if m.handlerOverrideRegisterValidator != nil {
+		m.handlerOverrideRegisterValidator(w, req)
 		return
 	}
 
@@ -166,9 +168,11 @@ func (m *mockRelay) MakeGetHeaderResponse(value uint64, hash, publicKey string)
 
 // handleGetHeader handles incoming requests to server.pathGetHeader
 func (m *mockRelay) handleGetHeader(w http.ResponseWriter, req *http.Request) {
+	m.mu.Lock()
+	defer m.mu.Unlock()
 	// Try to override default behavior is custom handler is specified.
-	if m.HandlerOverrideGetHeader != nil {
-		m.HandlerOverrideGetHeader(w, req)
+	if m.handlerOverrideGetHeader != nil {
+		m.handlerOverrideGetHeader(w, req)
 		return
 	}
 
@@ -208,9 +212,11 @@ func (m *mockRelay) MakeGetPayloadResponse(parentHash, blockHash, feeRecipient s
 
 // handleGetPayload handles incoming requests to server.pathGetPayload
 func (m *mockRelay) handleGetPayload(w http.ResponseWriter, req *http.Request) {
+	m.mu.Lock()
+	defer m.mu.Unlock()
 	// Try to override default behavior is custom handler is specified.
-	if m.HandlerOverrideGetPayload != nil {
-		m.HandlerOverrideGetPayload(w, req)
+	if m.handlerOverrideGetPayload != nil {
+		m.handlerOverrideGetPayload(w, req)
 		return
 	}
 
@@ -234,3 +240,10 @@ func (m *mockRelay) handleGetPayload(w http.ResponseWriter, req *http.Request) {
 		return
 	}
 }
+
+func (m *mockRelay) overrideHandleRegisterValidator(method func(w http.ResponseWriter, req *http.Request)) {
+	m.mu.Lock()
+	defer m.mu.Unlock()
+
+	m.handlerOverrideRegisterValidator = method
+}
```

### server/service_test.go
```diff
@@ -205,20 +205,18 @@ func TestRegisterValidator(t *testing.T) {
 		require.Equal(t, 1, backend.relays[1].GetRequestCount(path))
 
 		// Now make one relay return an error
-		backend.relays[0].HandlerOverrideRegisterValidator = func(w http.ResponseWriter,
-			r *http.Request) {
+		backend.relays[0].overrideHandleRegisterValidator(func(w http.ResponseWriter, r *http.Request) {
 			w.WriteHeader(http.StatusBadRequest)
-		}
+		})
 		rr = backend.request(t, http.MethodPost, path, payload)
 		require.Equal(t, http.StatusOK, rr.Code)
 		require.Equal(t, 2, backend.relays[0].GetRequestCount(path))
 		require.Equal(t, 2, backend.relays[1].GetRequestCount(path))
 
 		// Now make both relays return an error - which should cause the request to fail
-		backend.relays[1].HandlerOverrideRegisterValidator = func(w http.ResponseWriter,
-			r *http.Request) {
+		backend.relays[1].overrideHandleRegisterValidator(func(w http.ResponseWriter, r *http.Request) {
 			w.WriteHeader(http.StatusBadRequest)
-		}
+		})
 		rr = backend.request(t, http.MethodPost, path, payload)
 		require.Equal(t, `{"code":502,"message":"no successful relay response"}`+"\n", rr.Body.String())
 		require.Equal(t, http.StatusBadGateway, rr.Code)
```
