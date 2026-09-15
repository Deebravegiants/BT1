### Title
Missing allowlist/rate-limiting authorization on the WebAPI capabilities gateway legacy handler permits unauthenticated broadcast to all DON nodes - ([File: core/services/gateway/handlers/capabilities/handler.go])

### Summary
The `handler.HandleLegacyUserMessage` in the WebAPI capabilities gateway handler forwards any signature-valid but otherwise unauthorized/unallowlisted user message to every node in the DON, with an explicit `// TODO: apply allowlist and rate-limiting here` marking the missing check. [1](#0-0) 

### Finding Description
The CVE describes MCollective's `mco ping` allowing a remote, unauthenticated/unprivileged actor to broadcast a command to all managed nodes because the ping/broadcast path lacked adequate authorization checks. The analogous pattern here is the Chainlink WebAPI Gateway's legacy handler path: `gateway.ProcessRequest` decodes an incoming HTTP JSON-RPC request into an `api.Message`, calls `msg.Validate()` (which only checks structural fields and recovers the ECDSA signer of the message, `m.Body.Sender`), and dispatches it to the DON handler via `HandleLegacyUserMessage`. [2](#0-1) [3](#0-2) 

Inside `HandleLegacyUserMessage`, the code checks payload decodability and a staleness timestamp, then hits the comment `// TODO: apply allowlist and rate-limiting here` before unconditionally converting the message to a JSON-RPC request and calling `don.SendToNode` for **every member of the DON**:
```
// TODO: apply allowlist and rate-limiting here
...
for _, member := range h.donConfig.Members {
    err = errors.Join(err, don.SendToNode(ctx, member.Address, req))
}
``` [1](#0-0) 

`Message.Validate()` only verifies a well-formed, self-consistent ECDSA signature and extracts the signer address into `Sender` — it does not check that `Sender` is a permitted/allowlisted caller for the target DON or method. [3](#0-2)  Any actor capable of generating an ECDSA keypair (i.e., any unprivileged remote client) can self-sign an arbitrary message, pass `Validate()`, and have it fanned out to every DON node — functionally equivalent to the unauthenticated broadcast weakness in the MCollective `mco ping` bug class.

By contrast, other handlers in the same gateway package explicitly perform authorization/allowlist checks before fan-out — e.g. the Vault handler's `HandleJSONRPCUserMessage` calls `h.requestProcessor.ProcessRequest` (an `Authorizer.AuthorizeRequest` allowlist check) before dispatching to nodes, [4](#0-3)  and the WebAPI v2 trigger handler performs JWT-based authorization before sending to nodes. [5](#0-4)  The legacy capabilities handler is the outlier, lacking this control entirely, as the TODO comment self-documents.

### Impact Explanation
This handler broadcasts the (attacker-controlled) request payload to every node in the DON via `don.SendToNode`, without verifying the sender is an authorized workflow owner/caller. Depending on downstream node-side handling of `MethodWebAPITrigger`/target methods, this allows an unprivileged remote actor to trigger workflow execution paths on all DON nodes, consuming node resources, invoking arbitrary outbound HTTP requests via `handleWebAPIOutgoingMessage`/`sendHTTPMessageToClient` (SSRF-like exposure) once nodes echo actions back, and generally bypassing the intended access-control model for the gateway↔DON boundary. This matches the "unauthorized job run" and "allowlist bypass" criteria for a valid analog.

### Likelihood Explanation
The gateway HTTP endpoint (`gateway.ProcessRequest`) is internet-facing and reachable by any unauthenticated remote actor who can self-generate a signing key — there is no allowlist gate on `Sender`, only a signature well-formedness check. [6](#0-5)  Likelihood is high given the check is entirely absent (not weak — absent), as explicitly acknowledged by the inline TODO.

### Recommendation
Implement the sender allowlist/authorization check (and rate limiting) inside `HandleLegacyUserMessage` before fan-out to `don.SendToNode`, mirroring the pattern already used in the Vault (`requestProcessor.ProcessRequest`/`Authorizer.AuthorizeRequest`) and v2 HTTP trigger handlers (JWT-based `AuthorizedKey` check), so only permitted signers/workflow owners can trigger DON-wide broadcasts.

### Proof of Concept
1. Generate an arbitrary ECDSA keypair (no registration needed).
2. Construct an `api.Message` with `Body.Method = "web_api_trigger"`, a valid `Body.DonID`, a fresh timestamp payload, and sign it with `Message.Sign()`.
3. Submit as a legacy JSON-RPC request to the gateway HTTP endpoint (`gateway.ProcessRequest` path), which routes to `handler.HandleLegacyUserMessage` for the target DON.
4. Observe that the message passes `Validate()` and timestamp check, hits the TODO comment with no allowlist gate, and is forwarded via `don.SendToNode` to all `donConfig.Members`, despite the sender never being authorized or allowlisted for that DON/workflow. [1](#0-0)

### Citations

**File:** core/services/gateway/handlers/capabilities/handler.go (L384-420)
```go
	// TODO: apply allowlist and rate-limiting here
	if msg.Body.Method != MethodWebAPITrigger {
		h.lggr.Errorw("unsupported method", "method", body.Method)
		return callback.SendResponse(handlers.UserCallbackPayload{
			RawResponse: codec.EncodeNewErrorResponse(
				msg.Body.MessageID,
				api.ToJSONRPCErrorCode(api.UnsupportedMethodError),
				"invalid method "+msg.Body.Method,
				nil,
			),
			ErrorCode: api.UnsupportedMethodError,
		})
	}
	req, err := common.ValidatedRequestFromMessage(msg)
	if err != nil {
		h.lggr.Errorw(ErrTransformingMessageToRequest)
		return callback.SendResponse(handlers.UserCallbackPayload{
			RawResponse: codec.EncodeNewErrorResponse(
				msg.Body.MessageID,
				api.ToJSONRPCErrorCode(api.UserMessageParseError),
				ErrTransformingMessageToRequest,
				nil,
			),
			ErrorCode: api.UserMessageParseError,
		})
	}

	h.mu.Lock()
	h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
	don := h.don
	h.mu.Unlock()

	// Send original request to all nodes
	for _, member := range h.donConfig.Members {
		err = errors.Join(err, don.SendToNode(ctx, member.Address, req))
	}
	return err
```

**File:** core/services/gateway/gateway.go (L220-272)
```go
// Called by the server
func (g *gateway) ProcessRequest(ctx context.Context, rawRequest []byte, auth string) (rawResponse []byte, httpStatusCode int) {
	// decode
	jsonRequest, err := jsonrpc2.DecodeRequest[json.RawMessage](rawRequest, auth)
	if err != nil {
		return newError("", api.UserMessageParseError, err.Error())
	}
	msg, err := g.codec.DecodeJSONRequest(jsonRequest)
	if err != nil {
		return newError(jsonRequest.ID, api.UserMessageParseError, err.Error())
	}
	if len(jsonRequest.ID) > 200 {
		// Arbitrary limit to prevent abuse
		return newError(jsonRequest.ID, api.UserMessageParseError, "request ID is too long: "+strconv.Itoa(len(jsonRequest.ID))+". max is 200 characters")
	}
	isLegacyRequest := false
	var h handlers.Handler
	var handlerKey string
	if msg == nil || msg.Body.DonID == "" {
		serviceName := jsonRequest.ServiceName()
		if handler, ok := g.serviceToMultiHandler[serviceName]; ok {
			h = handler
			handlerKey = serviceName
		} else if donID, ok := g.serviceNameToDonID[serviceName]; ok {
			// Fallback to legacy service name -> DON ID mapping
			if handler, ok := g.handlers[donID]; ok {
				h = handler
				handlerKey = donID
			}
		}
		if h == nil {
			return newError(jsonRequest.ID, api.HandlerError, "Service name not found: "+serviceName)
		}
	} else {
		// Legacy request with DON ID - validate and fetch handler
		isLegacyRequest = true
		if err = msg.Validate(); err != nil {
			return newError(jsonRequest.ID, api.UserMessageParseError, err.Error())
		}
		handlerKey = msg.Body.DonID
		var ok bool
		h, ok = g.handlers[handlerKey]
		if !ok {
			return newError(jsonRequest.ID, api.UnsupportedDONIdError, "Unsupported DON ID: "+handlerKey)
		}
	}

	startTime := time.Now()
	var method string
	callback := handlerscommon.NewCallback()
	if isLegacyRequest {
		method = msg.Body.Method
		err = h.HandleLegacyUserMessage(ctx, msg, callback)
```

**File:** core/services/gateway/api/message.go (L54-88)
```go
func (m *Message) Validate() error {
	if m == nil {
		return errors.New("nil message")
	}
	if len(m.Signature) != MessageSignatureHexEncodedLen {
		return errors.New("invalid hex-encoded signature length")
	}
	if len(m.Body.MessageID) == 0 || len(m.Body.MessageID) > MessageIDMaxLen {
		return errors.New("invalid message ID length")
	}
	if strings.HasSuffix(m.Body.MessageID, NullChar) {
		return errors.New("message ID ending with null bytes")
	}
	if len(m.Body.Method) == 0 || len(m.Body.Method) > MessageMethodMaxLen {
		return errors.New("invalid method name length")
	}
	if strings.HasSuffix(m.Body.Method, NullChar) {
		return errors.New("method name ending with null bytes")
	}
	if len(m.Body.DonID) == 0 || len(m.Body.DonID) > MessageDonIDMaxLen {
		return errors.New("invalid DON ID length")
	}
	if strings.HasSuffix(m.Body.DonID, NullChar) {
		return errors.New("DON ID ending with null bytes")
	}
	if len(m.Body.Receiver) != 0 && len(m.Body.Receiver) != MessageReceiverLen {
		return errors.New("invalid Receiver length")
	}
	signerBytes, err := m.ExtractSigner()
	if err != nil {
		return err
	}
	m.Body.Sender = utils.StringToHex(string(signerBytes))
	return nil
}
```

**File:** core/services/gateway/handlers/vault/handler.go (L422-434)
```go
	if !vaulttypes.IsGatewaySecretsMethod(req.Method) {
		return h.sendImmediateUserResponse(ctx, req, callback, api.UnsupportedMethodError, errors.New("this method is unsupported: "+req.Method))
	}

	_, cachedPublicKey := h.getCachedPublicKey()
	authorized, err := h.requestProcessor.ProcessRequest(ctx, &req, cachedPublicKey)
	if err != nil {
		if vaultcap.IsInvalidVaultParamsError(err) {
			return h.sendImmediateUserResponse(ctx, req, callback, api.InvalidParamsError, err)
		}
		h.lggr.Errorw("request not authorized", "method", req.Method, "requestID", req.ID, "hasAuth", req.Auth != "", "error", err)
		return errors.New("request not authorized: " + err.Error())
	}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler_test.go (L1003-1059)
```go
func TestHttpTriggerHandler_HandleUserTriggerRequest_JWTAuthorization(t *testing.T) {
	handler, mockDon := createTestTriggerHandler(t)
	ctx := t.Context()

	// Setup metadata handler with test data
	err := handler.workflowMetadataHandler.aggs[handler.workflowMetadataHandler.shards[0].donID].Start(ctx)
	require.NoError(t, err)
	defer handler.workflowMetadataHandler.aggs[handler.workflowMetadataHandler.shards[0].donID].Close()

	// Create test keys
	privateKey := createTestPrivateKey(t)
	signerAddr := crypto.PubkeyToAddress(privateKey.PublicKey)

	// Add authorized key to metadata handler
	key := gateway_common.AuthorizedKey{
		KeyType:   gateway_common.KeyTypeECDSAEVM,
		PublicKey: strings.ToLower(signerAddr.Hex()),
	}
	handler.workflowMetadataHandler.authorizedKeys[workflowID] = map[gateway_common.AuthorizedKey]struct{}{key: {}}
	handler.workflowMetadataHandler.workflowIDToRef[workflowID] = workflowReference{
		workflowOwner: workflowOwner,
		workflowName:  "test-workflow",
		workflowTag:   "v1.0",
	}
	// Assign the workflow to all shards so setupCallback/sendWithRetries can
	// fan the request out (these tests populate the metadata maps directly
	// instead of calling registerWorkflow).
	assignWorkflowToAllShards(handler.workflowMetadataHandler, workflowID)

	t.Run("successful JWT authorization", func(t *testing.T) {
		callback := hc.NewCallback()

		triggerReq := createTestTriggerRequest(workflowID)
		reqBytes, err2 := json.Marshal(triggerReq)
		require.NoError(t, err2)

		rawParams := json.RawMessage(reqBytes)
		req := &jsonrpc.Request[json.RawMessage]{
			Version: "2.0",
			ID:      "test-request-id",
			Method:  gateway_common.MethodWorkflowExecute,
			Params:  &rawParams,
		}

		jwtToken := createTestJWTToken(t, req, privateKey)
		req.Auth = jwtToken

		mockDon.EXPECT().SendToNode(mock.Anything, "node1", mock.MatchedBy(func(r *jsonrpc.Request[json.RawMessage]) bool {
			var params gateway_common.HTTPTriggerRequest
			err = json.Unmarshal(*r.Params, &params)
			return err == nil && params.Key.PublicKey == key.PublicKey
		})).Return(nil)
		mockDon.EXPECT().SendToNode(mock.Anything, "node2", mock.Anything).Return(nil)
		mockDon.EXPECT().SendToNode(mock.Anything, "node3", mock.Anything).Return(nil)

		err = handler.HandleUserTriggerRequest(ctx, req, callback, time.Now())
		require.NoError(t, err)
```
