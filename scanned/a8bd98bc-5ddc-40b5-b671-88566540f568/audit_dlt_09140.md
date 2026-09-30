# [?] Vault Gateway Handler: Fix panic (#20030)

## Summary
Severity: Unknown
Chain: Chainlink
Component: smartcontractkit/chainlink
Published: 2025-10-22
Source: https://github.com/smartcontractkit/chainlink/commit/0245aef6fe1c090ae7e71ee12ab69490920b674d
Type: security-commit

## Details
Vault Gateway Handler: Fix panic (#20030)

* panic fix

* fix tooling

* test fixes and revert tooling changes

* nit error message fix

* respond to comments

## Patch
### core/services/gateway/handlers/vault/aggregator.go
```diff
@@ -5,6 +5,7 @@ import (
 	"encoding/json"
 	"errors"
 	"fmt"
+	"strconv"
 
 	"github.com/ethereum/go-ethereum/common"
 
@@ -19,7 +20,7 @@ type baseAggregator struct {
 	capabilitiesRegistry capabilitiesRegistry
 }
 
-func (a *baseAggregator) Aggregate(ctx context.Context, l logger.Logger, resps map[string]*jsonrpc.Response[json.RawMessage], currResp *jsonrpc.Response[json.RawMessage]) (*jsonrpc.Response[json.RawMessage], error) {
+func (a *baseAggregator) Aggregate(ctx context.Context, l logger.Logger, resps map[string]jsonrpc.Response[json.RawMessage], currResp *jsonrpc.Response[json.RawMessage]) (*jsonrpc.Response[json.RawMessage], error) {
 	don, err := a.donForVaultCapability(ctx)
 	if err != nil {
 		return nil, fmt.Errorf("failed to get DON for vault capability: %w", err)
@@ -55,7 +56,7 @@ func (a *baseAggregator) donForVaultCapability(ctx context.Context) (*capabiliti
 	return &don, nil
 }
 
-func (a *baseAggregator) validateUsingQuorum(don capabilities.DON, resps map[string]*jsonrpc.Response[json.RawMessage], l logger.Logger) (*jsonrpc.Response[json.RawMessage], error) {
+func (a *baseAggregator) validateUsingQuorum(don capabilities.DON, resps map[string]jsonrpc.Response[json.RawMessage], l logger.Logger) (*jsonrpc.Response[json.RawMessage], error) {
 	requiredQuorum := int(2*don.F + 1)
 
 	if len(resps) < requiredQuorum {
@@ -65,7 +66,7 @@ func (a *baseAggregator) validateUsingQuorum(don capabilities.DON, resps map[str
 	shaToCount := map[string]int{}
 	maxShaToCount := 0
 	for _, r := range resps {
-		sha, err := a.sha(r)
+		sha, err := a.sha(&r)
 		if err != nil {
 			l.Errorw("failed to compute digest of response during quorum validation, skipping...", "error", err)
 			continue
@@ -75,13 +76,13 @@ func (a *baseAggregator) validateUsingQuorum(don capabilities.DON, resps map[str
 			maxShaToCount = shaToCount[sha]
 		}
 		if shaToCount[sha] >= requiredQuorum {
-			return r, nil
+			return &r, nil
 		}
 	}
 
 	remainingResponses := len(don.Members) - len(resps)
 	if maxShaToCount+remainingResponses < requiredQuorum {
-		return nil, errQuorumUnobtainable
+		return nil, errors.New(errQuorumUnobtainable.Error() + ". RequiredQuorum=" + strconv.Itoa(requiredQuorum) + ". maxShaToCount=" + strconv.Itoa(maxShaToCount) + " remainingResponses=" + strconv.Itoa(remainingResponses))
 	}
 
 	return nil, errInsufficientResponsesForQuorum
```

### core/services/gateway/handlers/vault/aggregator_test.go
```diff
@@ -56,18 +56,18 @@ func TestAggregator_Valid_Signatures(t *testing.T) {
 	rawResp, err := json.Marshal(sor)
 	require.NoError(t, err)
 
-	currResp := &jsonrpc.Response[json.RawMessage]{
+	currResp := jsonrpc.Response[json.RawMessage]{
 		Version: jsonrpc.JsonRpcVersion,
 		ID:      "1",
 		Method:  vaulttypes.MethodSecretsCreate,
 		Result:  (*json.RawMessage)(&rawResp),
 	}
-	responses := map[string]*jsonrpc.Response[json.RawMessage]{
+	responses := map[string]jsonrpc.Response[json.RawMessage]{
 		"a": currResp,
 	}
-	resp, err := agg.Aggregate(t.Context(), logger.Test(t), responses, currResp)
+	resp, err := agg.Aggregate(t.Context(), logger.Test(t), responses, &currResp)
 	require.NoError(t, err)
-	assert.Equal(t, currResp, resp)
+	assert.Equal(t, &currResp, resp)
 }
 
 func mustRandom(length int) []byte {
@@ -116,7 +116,7 @@ func TestAggregator_Valid_FallsBackToQuorum(t *testing.T) {
 	mcr := &mockCapabilitiesRegistry{F: 1, Nodes: nodes}
 	agg := &baseAggregator{capabilitiesRegistry: mcr}
 
-	currResp := &jsonrpc.Response[json.RawMessage]{
+	currResp := jsonrpc.Response[json.RawMessage]{
 		Version: jsonrpc.JsonRpcVersion,
 		ID:      "1",
 		Method:  vaulttypes.MethodSecretsGet,
@@ -126,14 +126,14 @@ func TestAggregator_Valid_FallsBackToQuorum(t *testing.T) {
 			Message: "some error",
 		},
 	}
-	responses := map[string]*jsonrpc.Response[json.RawMessage]{
+	responses := map[string]jsonrpc.Response[json.RawMessage]{
 		"a": currResp,
 		"b": currResp,
 		"c": currResp,
 	}
-	resp, err := agg.Aggregate(t.Context(), logger.Test(t), responses, currResp)
+	resp, err := agg.Aggregate(t.Context(), logger.Test(t), responses, &currResp)
 	require.NoError(t, err)
-	assert.Equal(t, currResp, resp)
+	assert.Equal(t, &currResp, resp)
 }
 
 func TestAggregator_Valid_FallsBackToQuorum_ExcludesSignaturesInSha(t *testing.T) {
@@ -151,10 +151,10 @@ func TestAggregator_Valid_FallsBackToQuorum_ExcludesSignaturesInSha(t *testing.T
 	oldResp1 := newMessage(t)
 	oldResp2 := newMessage(t)
 	currResp := newMessage(t)
-	responses := map[string]*jsonrpc.Response[json.RawMessage]{
-		"a": oldResp1,
-		"b": oldResp2,
-		"c": currResp,
+	responses := map[string]jsonrpc.Response[json.RawMessage]{
+		"a": *oldResp1,
+		"b": *oldResp2,
+		"c": *currResp,
 	}
 	resp, err := agg.Aggregate(t.Context(), logger.Test(t), responses, currResp)
 	require.NoError(t, err)
@@ -177,16 +177,16 @@ func TestAggregator_InsufficientResponses(t *testing.T) {
 	agg := &baseAggregator{capabilitiesRegistry: mcr}
 
 	rm := json.RawMessage([]byte(`{}`))
-	currResp := &jsonrpc.Response[json.RawMessage]{
+	currResp := jsonrpc.Response[json.RawMessage]{
 		Version: jsonrpc.JsonRpcVersion,
 		ID:      "1",
 		Method:  vaulttypes.MethodSecretsGet,
 		Result:  &rm,
 	}
-	responses := map[string]*jsonrpc.Response[json.RawMessage]{
+	responses := map[string]jsonrpc.Response[json.RawMessage]{
 		"a": currResp,
 	}
-	_, err := agg.Aggregate(t.Context(), logger.Test(t), responses, currResp)
+	_, err := agg.Aggregate(t.Context(), logger.Test(t), responses, &currResp)
 	require.ErrorContains(t, err, "insufficient valid responses to reach quorum")
 }
 
@@ -223,10 +223,10 @@ func TestAggregator_QuorumUnobtainable(t *testing.T) {
 		Method:  vaulttypes.MethodSecretsGet,
 		Result:  &rm3,
 	}
-	responses := map[string]*jsonrpc.Response[json.RawMessage]{
-		"a": resp1,
-		"b": resp2,
-		"c": resp3,
+	responses := map[string]jsonrpc.Response[json.RawMessage]{
+		"a": *resp1,
+		"b": *resp2,
+		"c": *resp3,
 	}
 	_, err := agg.Aggregate(t.Context(), logger.Test(t), responses, resp3)
 	require.ErrorContains(t, err, "failed to validate using quorum: quorum unobtainable")
```

### core/services/gateway/handlers/vault/handler.go
```diff
@@ -94,11 +94,25 @@ func (ar *activeRequest) addResponseForNode(nodeAddr string, resp *jsonrpc.Respo
 	return true
 }
 
-func (ar *activeRequest) copiedResponses() map[string]*jsonrpc.Response[json.RawMessage] {
+func (ar *activeRequest) copiedResponses() map[string]jsonrpc.Response[json.RawMessage] {
 	ar.mu.Lock()
 	defer ar.mu.Unlock()
-	copied := make(map[string]*jsonrpc.Response[json.RawMessage], len(ar.responses))
-	maps.Copy(copied, ar.responses)
+	copied := make(map[string]jsonrpc.Response[json.RawMessage], len(ar.responses))
+	for k, response := range ar.responses {
+		var copiedResponse jsonrpc.Response[json.RawMessage]
+		if response != nil {
+			copiedResponse = *response
+			if response.Result != nil {
+				copiedResult := *response.Result
+				copiedResponse.Result = &copiedResult
+			}
+			if response.Error != nil {
+				copiedError := *response.Error
+				copiedResponse.Error = &copiedError
+			}
+		}
+		copied[k] = copiedResponse
+	}
 	return copied
 }
 
@@ -107,7 +121,7 @@ type capabilitiesRegistry interface {
 }
 
 type aggregator interface {
-	Aggregate(ctx context.Context, l logger.Logger, resps map[string]*jsonrpc.Response[json.RawMessage], currResp *jsonrpc.Response[json.RawMessage]) (*jsonrpc.Response[json.RawMessage], error)
+	Aggregate(ctx context.Context, l logger.Logger, resps map[string]jsonrpc.Response[json.RawMessage], currResp *jsonrpc.Response[json.RawMessage]) (*jsonrpc.Response[json.RawMessage], error)
 }
 
 type handler struct {
@@ -399,7 +413,8 @@ func (h *handler) HandleNodeMessage(ctx context.Context, resp *jsonrpc.Response[
 		return nil
 	}
 
-	resp, err := h.aggregator.Aggregate(ctx, l, ar.copiedResponses(), resp)
+	copiedResponses := ar.copiedResponses()
+	resp, err := h.aggregator.Aggregate(ctx, l, copiedResponses, resp)
 	switch {
 	case errors.Is(err, errInsufficientResponsesForQuorum):
 		l.Debugw("aggregating responses, waiting for other nodes...", "error", err)
```

### core/services/gateway/handlers/vault/handler_test.go
```diff
@@ -70,7 +70,7 @@ type mockAggregator struct {
 	err error
 }
 
-func (m *mockAggregator) Aggregate(_ context.Context, _ logger.Logger, _ map[string]*jsonrpc.Response[json.RawMessage], currResp *jsonrpc.Response[json.RawMessage]) (*jsonrpc.Response[json.RawMessage], error) {
+func (m *mockAggregator) Aggregate(_ context.Context, _ logger.Logger, _ map[string]jsonrpc.Response[json.RawMessage], currResp *jsonrpc.Response[json.RawMessage]) (*jsonrpc.Response[json.RawMessage], error) {
 	if m.err != nil {
 		return nil, m.err
 	}
```
