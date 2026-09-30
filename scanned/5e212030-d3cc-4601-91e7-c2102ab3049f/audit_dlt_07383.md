# [?] [CAPPL-324] Fix panic when fetching binary (#15490)

## Summary
Severity: Unknown
Chain: Chainlink
Component: smartcontractkit/chainlink
Published: 2024-12-04
Source: https://github.com/smartcontractkit/chainlink/commit/22c6cf7320d6bfb16e8132729ddd2efa3cbd2bb7
Type: security-commit

## Details
[CAPPL-324] Fix panic when fetching binary (#15490)

* Fix panic when fetching the binary

* [CAPPL-324] Fix panic when fetching the binary

* [fix] Various Gateway bugs

- Stop logging out the request/response body
- Add a timeout when fetching the request
- Add the method in various places where it was missing

* Fix test

* Linting

* Review comments

## Patch
### core/capabilities/webapi/outgoing_connector_handler.go
```diff
@@ -10,6 +10,7 @@ import (
 	"github.com/pkg/errors"
 
 	"github.com/smartcontractkit/chainlink-common/pkg/logger"
+	"github.com/smartcontractkit/chainlink-common/pkg/services"
 	"github.com/smartcontractkit/chainlink/v2/core/services/gateway/api"
 	"github.com/smartcontractkit/chainlink/v2/core/services/gateway/connector"
 	"github.com/smartcontractkit/chainlink/v2/core/services/gateway/handlers/capabilities"
@@ -19,6 +20,7 @@ import (
 var _ connector.GatewayConnectorHandler = &OutgoingConnectorHandler{}
 
 type OutgoingConnectorHandler struct {
+	services.StateMachine
 	gc            connector.GatewayConnector
 	method        string
 	lggr          logger.Logger
@@ -98,7 +100,7 @@ func (c *OutgoingConnectorHandler) HandleGatewayMessage(ctx context.Context, gat
 	}
 	l.Debugw("handling gateway request")
 	switch body.Method {
-	case capabilities.MethodWebAPITarget, capabilities.MethodComputeAction:
+	case capabilities.MethodWebAPITarget, capabilities.MethodComputeAction, capabilities.MethodWorkflowSyncer:
 		body := &msg.Body
 		var payload capabilities.Response
 		err := json.Unmarshal(body.Payload, &payload)
@@ -125,16 +127,28 @@ func (c *OutgoingConnectorHandler) HandleGatewayMessage(ctx context.Context, gat
 }
 
 func (c *OutgoingConnectorHandler) Start(ctx context.Context) error {
-	return c.gc.AddHandler([]string{c.method}, c)
+	return c.StartOnce("OutgoingConnectorHandler", func() error {
+		return c.gc.AddHandler([]string{c.method}, c)
+	})
 }
 
 func (c *OutgoingConnectorHandler) Close() error {
-	return nil
+	return c.StopOnce("OutgoingConnectorHandler", func() error {
+		return nil
+	})
+}
+
+func (c *OutgoingConnectorHandler) HealthReport() map[string]error {
+	return map[string]error{c.Name(): c.Healthy()}
+}
+
+func (c *OutgoingConnectorHandler) Name() string {
+	return c.lggr.Name()
 }
 
 func validMethod(method string) bool {
 	switch method {
-	case capabilities.MethodWebAPITarget, capabilities.MethodComputeAction:
+	case capabilities.MethodWebAPITarget, capabilities.MethodComputeAction, capabilities.MethodWorkflowSyncer:
 		return true
 	default:
 		return false
```

### core/services/chainlink/application.go
```diff
@@ -34,7 +34,6 @@ import (
 	gatewayconnector "github.com/smartcontractkit/chainlink/v2/core/capabilities/gateway_connector"
 	"github.com/smartcontractkit/chainlink/v2/core/capabilities/remote"
 	remotetypes "github.com/smartcontractkit/chainlink/v2/core/capabilities/remote/types"
-	"github.com/smartcontractkit/chainlink/v2/core/capabilities/webapi"
 	"github.com/smartcontractkit/chainlink/v2/core/chains/evm/logpoller"
 	"github.com/smartcontractkit/chainlink/v2/core/chains/evm/txmgr"
 	evmtypes "github.com/smartcontractkit/chainlink/v2/core/chains/evm/types"
@@ -50,8 +49,6 @@ import (
 	"github.com/smartcontractkit/chainlink/v2/core/services/feeds"
 	"github.com/smartcontractkit/chainlink/v2/core/services/fluxmonitorv2"
 	"github.com/smartcontractkit/chainlink/v2/core/services/gateway"
-	capabilities2 "github.com/smartcontractkit/chainlink/v2/core/services/gateway/handlers/capabilities"
-	common2 "github.com/smartcontractkit/chainlink/v2/core/services/gateway/handlers/common"
 	"github.com/smartcontractkit/chainlink/v2/core/services/headreporter"
 	"github.com/smartcontractkit/chainlink/v2/core/services/job"
 	"github.com/smartcontractkit/chainlink/v2/core/services/keeper"
@@ -303,30 +300,13 @@ func NewApplication(opts ApplicationOpts) (Application, error) {
 					return nil, fmt.Errorf("expected 1 key, got %d", len(keys))
 				}
 
-				connector := gatewayConnectorWrapper.GetGatewayConnector()
-				webAPILggr := globalLogger.Named("WebAPITarget")
-
-				webAPIConfig := webapi.ServiceConfig{
-					RateLimiter: common2.RateLimiterConfig{
-						GlobalRPS:      100.0,
-						GlobalBurst:    100,
-						PerSenderRPS:   100.0,
-						PerSenderBurst: 100,
-					},
-				}
-
-				outgoingConnectorHandler, err := webapi.NewOutgoingConnectorHandler(connector,
-					webAPIConfig,
-					capabilities2.MethodWebAPITarget, webAPILggr)
-				if err != nil {
-					return nil, fmt.Errorf("could not create outgoing connector handler: %w", err)
-				}
+				fetcher := syncer.NewFetcherService(globalLogger, gatewayConnectorWrapper)
 
 				eventHandler := syncer.NewEventHandler(globalLogger, syncer.NewWorkflowRegistryDS(opts.DS, globalLogger),
-					syncer.NewFetcherFunc(globalLogger, outgoingConnectorHandler), workflowstore.NewDBStore(opts.DS, globalLogger, clockwork.NewRealClock()), opts.CapabilitiesRegistry,
+					fetcher.Fetch, workflowstore.NewDBStore(opts.DS, globalLogger, clockwork.NewRealClock()), opts.CapabilitiesRegistry,
 					custmsg.NewLabeler(), clockwork.NewRealClock(), keys[0])
 
-				loader := syncer.NewWorkflowRegistryContractLoader(cfg.Capabilities().WorkflowRegistry().Address(), func(ctx context.Context, bytes []byte) (syncer.ContractReader, error) {
+				loader := syncer.NewWorkflowRegistryContractLoader(globalLogger, cfg.Capabilities().WorkflowRegistry().Address(), func(ctx context.Context, bytes []byte) (syncer.ContractReader, error) {
 					return relayer.NewContractReader(ctx, bytes)
 				}, eventHandler)
 
@@ -338,7 +318,7 @@ func NewApplication(opts ApplicationOpts) (Application, error) {
 						QueryCount: 100,
 					}, eventHandler, loader, workflowDonNotifier)
 
-				srvcs = append(srvcs, wfSyncer)
+				srvcs = append(srvcs, fetcher, wfSyncer)
 			}
 		}
 	} else {
```

### core/services/gateway/connector/connector.go
```diff
@@ -23,7 +23,7 @@ import (
 
 // GatewayConnector is a component run by Nodes to connect to a set of Gateways.
 type GatewayConnector interface {
-	job.ServiceCtx
+	services.Service
 	network.ConnectionInitiator
 
 	AddHandler(methods []string, handler GatewayConnectorHandler) error
```

### core/services/gateway/connector/mocks/gateway_connector.go
```diff
@@ -269,6 +269,98 @@ func (_c *GatewayConnector_GatewayIDs_Call) RunAndReturn(run func() []string) *G
 	return _c
 }
 
+// HealthReport provides a mock function with given fields:
+func (_m *GatewayConnector) HealthReport() map[string]error {
+	ret := _m.Called()
+
+	if len(ret) == 0 {
+		panic("no return value specified for HealthReport")
+	}
+
+	var r0 map[string]error
+	if rf, ok := ret.Get(0).(func() map[string]error); ok {
+		r0 = rf()
+	} else {
+		if ret.Get(0) != nil {
+			r0 = ret.Get(0).(map[string]error)
+		}
+	}
+
+	return r0
+}
+
+// GatewayConnector_HealthReport_Call is a *mock.Call that shadows Run/Return methods with type explicit version for method 'HealthReport'
+type GatewayConnector_HealthReport_Call struct {
+	*mock.Call
+}
+
+// HealthReport is a helper method to define mock.On call
+func (_e *GatewayConnector_Expecter) HealthReport() *GatewayConnector_HealthReport_Call {
+	return &GatewayConnector_HealthReport_Call{Call: _e.mock.On("HealthReport")}
+}
+
+func (_c *GatewayConnector_HealthReport_Call) Run(run func()) *GatewayConnector_HealthReport_Call {
+	_c.Call.Run(func(args mock.Arguments) {
+		run()
+	})
+	return _c
+}
+
+func (_c *GatewayConnector_HealthReport_Call) Return(_a0 map[string]error) *GatewayConnector_HealthReport_Call {
+	_c.Call.Return(_a0)
+	return _c
+}
+
+func (_c *GatewayConnector_HealthReport_Call) RunAndReturn(run func() map[string]error) *GatewayConnector_HealthReport_Call {
+	_c.Call.Return(run)
+	return _c
+}
+
+// Name provides a mock function with given fields:
+func (_m *GatewayConnector) Name() string {
+	ret := _m.Called()
+
+	if len(ret) == 0 {
+		panic("no return value specified for Name")
+	}
+
+	var r0 string
+	if rf, ok := ret.Get(0).(func() string); ok {
+		r0 = rf()
+	} else {
+		r0 = ret.Get(0).(string)
+	}
+
+	return r0
+}
+
+// GatewayConnector_Name_Call is a *mock.Call that shadows Run/Return methods with type explicit version for method 'Name'
+type GatewayConnector_Name_Call struct {
+	*mock.Call
+}
+
+// Name is a helper method to define mock.On call
+func (_e *GatewayConnector_Expecter) Name() *GatewayConnector_Name_Call {
+	return &GatewayConnector_Name_Call{Call: _e.mock.On("Name")}
+}
+
+func (_c *GatewayConnector_Name_Call) Run(run func()) *GatewayConnector_Name_Call {
+	_c.Call.Run(func(args mock.Arguments) {
+		run()
+	})
+	return _c
+}
+
+func (_c *GatewayConnector_Name_Call) Return(_a0 string) *GatewayConnector_Name_Call {
+	_c.Call.Return(_a0)
+	return _c
+}
+
+func (_c *GatewayConnector_Name_Call) RunAndReturn(run func() string) *GatewayConnector_Name_Call {
+	_c.Call.Return(run)
+	return _c
+}
+
 // NewAuthHeader provides a mock function with given fields: _a0
 func (_m *GatewayConnector) NewAuthHeader(_a0 *url.URL) ([]byte, error) {
 	ret := _m.Called(_a0)
@@ -327,6 +419,51 @@ func (_c *GatewayConnector_NewAuthHeader_Call) RunAndReturn(run func(*url.URL) (
 	return _c
 }
 
+// Ready provides a mock function with given fields:
+func (_m *GatewayConnector) Ready() error {
+	ret := _m.Called()
+
+	if len(ret) == 0 {
+		panic("no return value specified for Ready")
+	}
+
+	var r0 error
+	if rf, ok := ret.Get(0).(func() error); ok {
+		r0 = rf()
+	} else {
+		r0 = ret.Error(0)
+	}
+
+	return r0
+}
+
+// GatewayConnector_Ready_Call is a *mock.Call that shadows Run/Return methods with type explicit version for method 'Ready'
+type GatewayConnector_Ready_Call struct {
+	*mock.Call
+}
+
+// Ready is a helper method to define mock.On call
+func (_e *GatewayConnector_Expecter) Ready() *GatewayConnector_Ready_Call {
+	return &GatewayConnector_Ready_Call{Call: _e.mock.On("Ready")}
+}
+
+func (_c *GatewayConnector_Ready_Call) Run(run func()) *GatewayConnector_Ready_Call {
+	_c.Call.Run(func(args mock.Arguments) {
+		run()
+	})
+	return _c
+}
+
+func (_c *GatewayConnector_Ready_Call) Return(_a0 error) *GatewayConnector_Ready_Call {
+	_c.Call.Return(_a0)
+	return _c
+}
+
+func (_c *GatewayConnector_Ready_Call) RunAndReturn(run func() error) *GatewayConnector_Ready_Call {
+	_c.Call.Return(run)
+	return _c
+}
+
 // SendToGateway provides a mock function with given fields: ctx, gatewayId, msg
 func (_m *GatewayConnector) SendToGateway(ctx context.Context, gatewayId string, msg *api.Message) error {
 	ret := _m.Called(ctx, gatewayId, msg)
```

### core/services/gateway/handlers/capabilities/handler.go
```diff
@@ -146,7 +146,8 @@ func (h *handler) handleWebAPIOutgoingMessage(ctx context.Context, msg *api.Mess
 		newCtx := context.WithoutCancel(ctx)
 		newCtx, cancel := context.WithTimeout(newCtx, timeout)
 		defer cancel()
-		l := h.lggr.With("url", payload.URL, "messageId", msg.Body.MessageId, "method", payload.Method)
+		l := h.lggr.With("url", payload.URL, "messageId", msg.Body.MessageId, "method", payload.Method, "timeout", payload.TimeoutMs)
+		l.Debug("Sending request to client")
 		respMsg, err := h.sendHTTPMessageToClient(newCtx, req, msg)
 		if err != nil {
 			l.Errorw("error while sending HTTP request to external endpoint", "err", err)
@@ -187,7 +188,7 @@ func (h *handler) HandleNodeMessage(ctx context.Context, msg *api.Message, nodeA
 	switch msg.Body.Method {
 	case MethodWebAPITrigger:
 		return h.handleWebAPITriggerMessage(ctx, msg, nodeAddr)
-	case MethodWebAPITarget, MethodComputeAction:
+	case MethodWebAPITarget, MethodComputeAction, MethodWorkflowSyncer:
 		return h.handleWebAPIOutgoingMessage(ctx, msg, nodeAddr)
 	default:
 		return fmt.Errorf("unsupported method: %s", msg.Body.Method)
```

### core/services/gateway/network/httpclient.go
```diff
@@ -78,7 +78,7 @@ func (c *httpClient) Send(ctx context.Context, req HTTPRequest) (*HTTPResponse,
 		// joining them to a single string in case array size is greater than 1
 		headers[k] = strings.Join(v, ",")
 	}
-	c.lggr.Debugw("received HTTP response", "statusCode", resp.StatusCode, "body", string(body), "url", req.URL, "headers", headers)
+	c.lggr.Debugw("received HTTP response", "statusCode", resp.StatusCode, "url", req.URL, "headers", headers)
 
 	return &HTTPResponse{
 		Headers:    headers,
```

### core/services/relay/evm/capabilities/workflows/syncer/workflow_syncer_test.go
```diff
@@ -98,7 +98,7 @@ func Test_InitialStateSync(t *testing.T) {
 	}
 
 	testEventHandler := newTestEvtHandler()
-	loader := syncer.NewWorkflowRegistryContractLoader(wfRegistryAddr.Hex(), func(ctx context.Context, bytes []byte) (syncer.ContractReader, error) {
+	loader := syncer.NewWorkflowRegistryContractLoader(lggr, wfRegistryAddr.Hex(), func(ctx context.Context, bytes []byte) (syncer.ContractReader, error) {
 		return backendTH.NewContractReader(ctx, t, bytes)
 	}, testEventHandler)
 
```

### core/services/workflows/syncer/fetcher.go
```diff
@@ -2,41 +2,113 @@ package syncer
 
 import (
 	"context"
+	"crypto/sha256"
+	"encoding/hex"
 	"encoding/json"
 	"fmt"
 	"net/http"
 	"strings"
 
+	"github.com/smartcontractkit/chainlink-common/pkg/services"
 	"github.com/smartcontractkit/chainlink/v2/core/capabilities/webapi"
 	"github.com/smartcontractkit/chainlink/v2/core/logger"
+	"github.com/smartcontractkit/chainlink/v2/core/services/gateway/connector"
+	"github.com/smartcontractkit/chainlink/v2/core/services/gateway/handlers/capabilities"
 	ghcapabilities "github.com/smartcontractkit/chainlink/v2/core/services/gateway/handlers/capabilities"
+	"github.com/smartcontractkit/chainlink/v2/core/services/gateway/handlers/common"
 )
 
-func NewFetcherFunc(
-	lggr logger.Logger,
-	och *webapi.OutgoingConnectorHandler) FetcherFunc {
-	return func(ctx context.Context, url string) ([]byte, error) {
-		payloadBytes, err := json.Marshal(ghcapabilities.Request{
-			URL:    url,
-			Method: http.MethodGet,
-		})
-		if err != nil {
-			return nil, fmt.Errorf("failed to marshal fetch request: %w", err)
-		}
+const (
+	defaultFetchTimeoutMs = 20_000
+)
 
-		messageID := strings.Join([]string{ghcapabilities.MethodWorkflowSyncer, url}, "/")
-		resp, err := och.HandleSingleNodeRequest(ctx, messageID, payloadBytes)
-		if err != nil {
-			return nil, err
+type FetcherService struct {
+	services.StateMachine
+	lggr    logger.Logger
+	och     *webapi.OutgoingConnectorHandler
+	wrapper gatewayConnector
+}
+
+type gatewayConnector interface {
+	GetGatewayConnector() connector.GatewayConnector
+}
+
+func NewFetcherService(lggr logger.Logger, wrapper gatewayConnector) *FetcherService {
+	return &FetcherService{
+		lggr:    lggr.Named("FetcherService"),
+		wrapper: wrapper,
+	}
+}
+
+func (s *FetcherService) Start(ctx context.Context) error {
+	return s.StartOnce("FetcherService", func() error {
+		connector := s.wrapper.GetGatewayConnector()
+
+		outgoingConnectorLggr := s.lggr.Named("WorkflowSyncer")
+
+		webAPIConfig := webapi.ServiceConfig{
+			RateLimiter: common.RateLimiterConfig{
+				GlobalRPS:      100.0,
+				GlobalBurst:    100,
+				PerSenderRPS:   100.0,
+				PerSenderBurst: 100,
+			},
 		}
 
-		lggr.Debugw("received gateway response", "resp", resp)
-		var payload ghcapabilities.Response
-		err = json.Unmarshal(resp.Body.Payload, &payload)
+		och, err := webapi.NewOutgoingConnectorHandler(connector,
+			webAPIConfig,
+			capabilities.MethodWorkflowSyncer, outgoingConnectorLggr)
 		if err != nil {
-			return nil, err
+			return fmt.Errorf("could not create outgoing connector handler: %w", err)
 		}
 
-		return payload.Body, nil
+		s.och = och
+		return och.Start(ctx)
+	})
+}
+
+func (s *FetcherService) Close() error {
+	return s.StopOnce("FetcherService", func() error {
+		return s.och.Close()
+	})
+}
+
+func (s *FetcherService) HealthReport() map[string]error {
+	return map[string]error{s.Name(): s.Healthy()}
+}
+
+func (s *FetcherService) Name() string {
+	return s.lggr.Name()
+}
+
+func hash(url string) string {
+	h := sha256.New()
+	h.Write([]byte(url))
+	return hex.EncodeToString(h.Sum(nil))
+}
+
+func (s *FetcherService) Fetch(ctx context.Context, url string) ([]byte, error) {
+	payloadBytes, err := json.Marshal(ghcapabilities.Request{
+		URL:       url,
+		Method:    http.MethodGet,
+		TimeoutMs: defaultFetchTimeoutMs,
+	})
+	if err != nil {
+		return nil, fmt.Errorf("failed to marshal fetch request: %w", err)
+	}
+
+	messageID := strings.Join([]string{ghcapabilities.MethodWorkflowSyncer, hash(url)}, "/")
+	resp, err := s.och.HandleSingleNodeRequest(ctx, messageID, payloadBytes)
+	if err != nil {
+		return nil, err
 	}
+
+	s.lggr.Debugw("received gateway response")
+	var payload ghcapabilities.Response
+	err = json.Unmarshal(resp.Body.Payload, &payload)
+	if err != nil {
+		return nil, err
+	}
+
+	return payload.Body, nil
 }
```

### core/services/workflows/syncer/fetcher_test.go
```diff
@@ -9,46 +9,48 @@ import (
 	"github.com/stretchr/testify/mock"
 	"github.com/stretchr/testify/require"
 
-	"github.com/smartcontractkit/chainlink/v2/core/capabilities/webapi"
 	"github.com/smartcontractkit/chainlink/v2/core/logger"
 	"github.com/smartcontractkit/chainlink/v2/core/services/gateway/api"
+	"github.com/smartcontractkit/chainlink/v2/core/services/gateway/connector"
 	gcmocks "github.com/smartcontractkit/chainlink/v2/core/services/gateway/connector/mocks"
+	"github.com/smartcontractkit/chainlink/v2/core/services/gateway/handlers/capabilities"
 	ghcapabilities "github.com/smartcontractkit/chainlink/v2/core/services/gateway/handlers/capabilities"
-	"github.com/smartcontractkit/chainlink/v2/core/services/gateway/handlers/common"
 )
 
-func TestNewFetcherFunc(t *testing.T) {
+type wrapper struct {
+	c connector.GatewayConnector
+}
+
+func (w *wrapper) GetGatewayConnector() connector.GatewayConnector {
+	return w.c
+}
+
+func TestNewFetcherService(t *testing.T) {
 	ctx := context.Background()
 	lggr := logger.TestLogger(t)
 
-	config := webapi.ServiceConfig{
-		RateLimiter: common.RateLimiterConfig{
-			GlobalRPS:      100.0,
-			GlobalBurst:    100,
-			PerSenderRPS:   100.0,
-			PerSenderBurst: 100,
-		},
-	}
-
 	connector := gcmocks.NewGatewayConnector(t)
-	och, err := webapi.NewOutgoingConnectorHandler(connector, config, ghcapabilities.MethodComputeAction, lggr)
-	require.NoError(t, err)
+	wrapper := &wrapper{c: connector}
 
 	url := "http://example.com"
 
-	msgID := strings.Join([]string{ghcapabilities.MethodWorkflowSyncer, url}, "/")
+	msgID := strings.Join([]string{ghcapabilities.MethodWorkflowSyncer, hash(url)}, "/")
 
 	t.Run("OK-valid_request", func(t *testing.T) {
+		connector.EXPECT().AddHandler([]string{capabilities.MethodWorkflowSyncer}, mock.Anything).Return(nil)
+
+		fetcher := NewFetcherService(lggr, wrapper)
+		require.NoError(t, fetcher.Start(ctx))
+		defer fetcher.Close()
+
 		gatewayResp := gatewayResponse(t, msgID)
 		connector.EXPECT().SignAndSendToGateway(mock.Anything, "gateway1", mock.Anything).Run(func(ctx context.Context, gatewayID string, msg *api.MessageBody) {
-			och.HandleGatewayMessage(ctx, "gateway1", gatewayResp)
+			fetcher.och.HandleGatewayMessage(ctx, "gateway1", gatewayResp)
 		}).Return(nil).Times(1)
 		connector.EXPECT().DonID().Return("don-id")
 		connector.EXPECT().GatewayIDs().Return([]string{"gateway1", "gateway2"})
 
-		fetcher := NewFetcherFunc(lggr, och)
-
-		payload, err := fetcher(ctx, url)
+		payload, err := fetcher.Fetch(ctx, url)
 		require.NoError(t, err)
 
 		expectedPayload := []byte("response body")
```

### core/services/workflows/syncer/workflow_registry.go
```diff
@@ -556,17 +556,20 @@ func (r workflowAsEvent) GetData() any {
 }
 
 type workflowRegistryContractLoader struct {
+	lggr                    logger.Logger
 	workflowRegistryAddress string
 	newContractReaderFn     newContractReaderFn
 	handler                 evtHandler
 }
 
 func NewWorkflowRegistryContractLoader(
+	lggr logger.Logger,
 	workflowRegistryAddress string,
 	newContractReaderFn newContractReaderFn,
 	handler evtHandler,
 ) *workflowRegistryContractLoader {
 	return &workflowRegistryContractLoader{
+		lggr:                    lggr.Named("WorkflowRegistryContractLoader"),
 		workflowRegistryAddress: workflowRegistryAddress,
 		newContractReaderFn:     newContractReaderFn,
 		handler:                 handler,
@@ -624,6 +627,7 @@ func (l *workflowRegistryContractLoader) LoadWorkflows(ctx context.Context, don
 			return nil, fmt.Errorf("failed to get workflow metadata for don %w", err)
 		}
 
+		l.lggr.Debugw("Rehydrating existing workflows", "len", len(workflows.WorkflowMetadataList))
 		for _, workflow := range workflows.WorkflowMetadataList {
 			if err = l.handler.Handle(ctx, workflowAsEvent{
 				Data:      workflow,
```

### core/services/workflows/syncer/workflow_registry_test.go
```diff
@@ -72,7 +72,7 @@ func Test_Workflow_Registry_Syncer(t *testing.T) {
 
 		handler = NewEventHandler(lggr, orm, gateway, nil, nil,
 			emitter, clockwork.NewFakeClock(), workflowkey.Key{})
-		loader = NewWorkflowRegistryContractLoader(contractAddress, func(ctx context.Context, bytes []byte) (ContractReader, error) {
+		loader = NewWorkflowRegistryContractLoader(lggr, contractAddress, func(ctx context.Context, bytes []byte) (ContractReader, error) {
 			return reader, nil
 		}, handler)
 
```
