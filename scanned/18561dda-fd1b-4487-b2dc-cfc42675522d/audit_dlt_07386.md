# [?] KS-384 add better logging for when payload changes per message id and fix client non-deterministic serialisation of remote target (#13877)

## Summary
Severity: Unknown
Chain: Chainlink
Component: smartcontractkit/chainlink
Published: 2024-07-18
Source: https://github.com/smartcontractkit/chainlink/commit/81a21bb56cd597858221f775c796994be0f2e0da
Type: security-commit

## Details
KS-384 add better logging for when payload changes per message id and fix client non-deterministic serialisation of remote target (#13877)

* improve logging when different payloads for the same message received and fix non-deterministic serialisation

* lint

## Patch
### .changeset/shiny-ligers-compete.md
```diff
@@ -0,0 +1,5 @@
+---
+"chainlink": patch
+---
+
+#internal logging of non determinism in target server
```

### core/capabilities/remote/target/request/client_request.go
```diff
@@ -8,6 +8,8 @@ import (
 	"sync"
 	"time"
 
+	"google.golang.org/protobuf/proto"
+
 	ragep2ptypes "github.com/smartcontractkit/libocr/ragep2p/types"
 
 	"github.com/smartcontractkit/chainlink-common/pkg/capabilities"
@@ -46,7 +48,8 @@ func NewClientRequest(ctx context.Context, lggr logger.Logger, req commoncap.Cap
 		return nil, errors.New("remote capability info missing DON")
 	}
 
-	rawRequest, err := pb.MarshalCapabilityRequest(req)
+	rawRequest, err := proto.MarshalOptions{Deterministic: true}.Marshal(pb.CapabilityRequestToProto(req))
+
 	if err != nil {
 		return nil, fmt.Errorf("failed to marshal capability request: %w", err)
 	}
```

### core/capabilities/remote/target/server.go
```diff
@@ -32,9 +32,12 @@ type server struct {
 	workflowDONs map[uint32]commoncap.DON
 	dispatcher   types.Dispatcher
 
-	requestIDToRequest map[string]*request.ServerRequest
+	requestIDToRequest map[string]requestAndMsgID
 	requestTimeout     time.Duration
 
+	// Used to detect messages with the same message id but different payloads
+	messageIDToRequestIDsCount map[string]map[string]int
+
 	receiveLock sync.Mutex
 	stopCh      services.StopChan
 	wg          sync.WaitGroup
@@ -43,6 +46,11 @@ type server struct {
 var _ types.Receiver = &server{}
 var _ services.Service = &server{}
 
+type requestAndMsgID struct {
+	request   *request.ServerRequest
+	messageID string
+}
+
 func NewServer(peerID p2ptypes.PeerID, underlying commoncap.TargetCapability, capInfo commoncap.CapabilityInfo, localDonInfo commoncap.DON,
 	workflowDONs map[uint32]commoncap.DON, dispatcher types.Dispatcher, requestTimeout time.Duration, lggr logger.Logger) *server {
 	return &server{
@@ -53,8 +61,9 @@ func NewServer(peerID p2ptypes.PeerID, underlying commoncap.TargetCapability, ca
 		workflowDONs: workflowDONs,
 		dispatcher:   dispatcher,
 
-		requestIDToRequest: map[string]*request.ServerRequest{},
-		requestTimeout:     requestTimeout,
+		requestIDToRequest:         map[string]requestAndMsgID{},
+		messageIDToRequestIDsCount: map[string]map[string]int{},
+		requestTimeout:             requestTimeout,
 
 		lggr:   lggr.Named("TargetServer"),
 		stopCh: make(services.StopChan),
@@ -96,12 +105,13 @@ func (r *server) expireRequests() {
 	defer r.receiveLock.Unlock()
 
 	for requestID, executeReq := range r.requestIDToRequest {
-		if executeReq.Expired() {
-			err := executeReq.Cancel(types.Error_TIMEOUT, "request expired")
+		if executeReq.request.Expired() {
+			err := executeReq.request.Cancel(types.Error_TIMEOUT, "request expired")
 			if err != nil {
 				r.lggr.Errorw("failed to cancel request", "request", executeReq, "err", err)
 			}
 			delete(r.requestIDToRequest, requestID)
+			delete(r.messageIDToRequestIDsCount, executeReq.messageID)
 		}
 	}
 }
@@ -122,22 +132,38 @@ func (r *server) Receive(ctx context.Context, msg *types.MessageBody) {
 	hash := sha256.Sum256(msg.Payload)
 	requestID := messageId + hex.EncodeToString(hash[:])
 
+	if requestIDs, ok := r.messageIDToRequestIDsCount[messageId]; ok {
+		requestIDs[requestID] = requestIDs[requestID] + 1
+	} else {
+		r.messageIDToRequestIDsCount[messageId] = map[string]int{requestID: 1}
+	}
+
+	requestIDs := r.messageIDToRequestIDsCount[messageId]
+	if len(requestIDs) > 1 {
+		// This is a potential attack vector as well as a situation that will occur if the client is sending non-deterministic payloads
+		// so a warning is logged
+		r.lggr.Warnw("received messages with the same id and different payloads", "messageID", messageId, "requestIDToCount", requestIDs)
+	}
+
 	if _, ok := r.requestIDToRequest[requestID]; !ok {
 		callingDon, ok := r.workflowDONs[msg.CallerDonId]
 		if !ok {
 			r.lggr.Errorw("received request from unregistered don", "donId", msg.CallerDonId)
 			return
 		}
 
-		r.requestIDToRequest[requestID] = request.NewServerRequest(r.underlying, r.capInfo.ID, r.localDonInfo.ID, r.peerID,
-			callingDon, messageId, r.dispatcher, r.requestTimeout, r.lggr)
+		r.requestIDToRequest[requestID] = requestAndMsgID{
+			request: request.NewServerRequest(r.underlying, r.capInfo.ID, r.localDonInfo.ID, r.peerID,
+				callingDon, messageId, r.dispatcher, r.requestTimeout, r.lggr),
+			messageID: messageId,
+		}
 	}
 
-	req := r.requestIDToRequest[requestID]
+	reqAndMsgID := r.requestIDToRequest[requestID]
 
-	err := req.OnMessage(ctx, msg)
+	err := reqAndMsgID.request.OnMessage(ctx, msg)
 	if err != nil {
-		r.lggr.Errorw("request failed to OnMessage new message", "request", req, "err", err)
+		r.lggr.Errorw("request failed to OnMessage new message", "request", reqAndMsgID, "err", err)
 	}
 }
 
```
