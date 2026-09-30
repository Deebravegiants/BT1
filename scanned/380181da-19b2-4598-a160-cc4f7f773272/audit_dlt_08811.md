# [?] Merge pull request #2304 from 0xPolygonHermez/improve/websocket-server-dos-prevention

## Summary
Severity: Unknown
Chain: Polygon zkEVM
Component: 0xPolygon/zkevm-node
Published: 2023-08-22
Source: https://github.com/0xPolygon/zkevm-node/commit/101da0153e1a6a1d583806006ec9998d76419129
Type: security-commit

## Details
Merge pull request #2304 from 0xPolygonHermez/improve/websocket-server-dos-prevention

Add WebSocket Read Limit

## Patch
### config/config_test.go
```diff
@@ -333,6 +333,10 @@ func Test_Defaults(t *testing.T) {
 			path:          "RPC.WebSockets.Port",
 			expectedValue: int(8546),
 		},
+		{
+			path:          "RPC.WebSockets.ReadLimit",
+			expectedValue: int64(104857600),
+		},
 		{
 			path:          "Executor.URI",
 			expectedValue: "zkevm-prover:50071",
```

### config/default.go
```diff
@@ -89,6 +89,7 @@ TraceBatchUseHTTPS = true
 		Enabled = true
 		Host = "0.0.0.0"
 		Port = 8546
+		ReadLimit = 104857600
 
 [Synchronizer]
 SyncInterval = "1s"
```

### docs/config-file/node-config-doc.html
```diff
@@ -14,7 +14,7 @@
 </pre></div> </div><div id=RPC_ReadTimeout_ex2 class="jumbotron examples"><div class=highlight><pre><span></span><span class=s2>&quot;300ms&quot;</span>
 </pre></div> </div> <hr> <div class=breadcrumbs> <!-- None --><!-- None --><a href=#RPC.WriteTimeout onclick="anchorLink('RPC.WriteTimeout')">RPC.WriteTimeout=</a> </div> <span class="badge badge-success default-value">Default: "1m0s"</span><span class="badge badge-dark value-type">Type: string</span><br> <span class=description><p>WriteTimeout is the HTTP server write timeout<br> check net/http.server.WriteTimeout</p> </span> <br> <div class="badge badge-secondary">Examples:</div> <br><div id=RPC_WriteTimeout_ex1 class="jumbotron examples"><div class=highlight><pre><span></span><span class=s2>&quot;1m&quot;</span>
 </pre></div> </div><div id=RPC_WriteTimeout_ex2 class="jumbotron examples"><div class=highlight><pre><span></span><span class=s2>&quot;300ms&quot;</span>
-</pre></div> </div> <hr> <div class=breadcrumbs> <!-- None --><!-- None --><a href=#RPC.MaxRequestsPerIPAndSecond onclick="anchorLink('RPC.MaxRequestsPerIPAndSecond')">RPC.MaxRequestsPerIPAndSecond=</a> </div> <span class="badge badge-success default-value">Default: 500</span><span class="badge badge-dark value-type">Type: number</span><br> <span class=description><p>MaxRequestsPerIPAndSecond defines how much requests a single IP can<br> send within a single second</p> </span> <hr> <div class=breadcrumbs> <!-- None --><!-- None --><a href=#RPC.SequencerNodeURI onclick="anchorLink('RPC.SequencerNodeURI')">RPC.SequencerNodeURI=</a> </div> <span class="badge badge-success default-value">Default: ""</span><span class="badge badge-dark value-type">Type: string</span><br> <span class=description><p>SequencerNodeURI is used allow Non-Sequencer nodes<br> to relay transactions to the Sequencer node</p> </span> <hr> <div class=breadcrumbs> <!-- None --><!-- None --><a href=#RPC.MaxCumulativeGasUsed onclick="anchorLink('RPC.MaxCumulativeGasUsed')">RPC.MaxCumulativeGasUsed=</a> </div> <span class="badge badge-success default-value">Default: 0</span><span class="badge badge-dark value-type">Type: integer</span><br> <span class=description><p>MaxCumulativeGasUsed is the max gas allowed per batch</p> </span> <hr> <div class=accordion id=accordionRPC_WebSockets> <div class=card> <div class=card-header id=headingRPC_WebSockets> <h2 class=mb-0> <button class="btn btn-link property-name-button" type=button data-toggle=collapse data-target=#RPC_WebSockets aria-expanded aria-controls=RPC_WebSockets onclick="setAnchor('#RPC_WebSockets')"><span class=property-name> <div class=breadcrumbs>[<a href=#RPC onclick="anchorLink('RPC')">RPC</a> . <a href=#RPC_WebSockets onclick="anchorLink('RPC_WebSockets')">WebSockets</a>] </div></span></button> </h2> WebSockets configuration </div> <div id=RPC_WebSockets class="collapse property-definition-div" aria-labelledby=headingRPC_WebSockets data-parent=#accordionRPC_WebSockets> <div class="card-body pl-5"> <div class=breadcrumbs> <!-- None --><!-- None --><!-- None --><a href=#RPC.WebSockets.Enabled onclick="anchorLink('RPC.WebSockets.Enabled')">RPC.WebSockets.Enabled=</a> </div> <span class="badge badge-success default-value">Default: true</span><span class="badge badge-dark value-type">Type: boolean</span><br> <span class=description><p>Enabled defines if the WebSocket requests are enabled or disabled</p> </span> <hr> <div class=breadcrumbs> <!-- None --><!-- None --><!-- None --><a href=#RPC.WebSockets.Host onclick="anchorLink('RPC.WebSockets.Host')">RPC.WebSockets.Host=</a> </div> <span class="badge badge-success default-value">Default: "0.0.0.0"</span><span class="badge badge-dark value-type">Type: string</span><br> <span class=description><p>Host defines the network adapter that will be used to serve the WS requests</p> </span> <hr> <div class=breadcrumbs> <!-- None --><!-- None --><!-- None --><a href=#RPC.WebSockets.Port onclick="anchorLink('RPC.WebSockets.Port')">RPC.WebSockets.Port=</a> </div> <span class="badge badge-success default-value">Default: 8546</span><span class="badge badge-dark value-type">Type: integer</span><br> <span class=description><p>Port defines the port to serve the endpoints via WS</p> </span> <hr> </div> </div> </div> </div> <div class=breadcrumbs> <!-- None --><!-- None --><a href=#RPC.EnableL2SuggestedGasPricePolling onclick="anchorLink('RPC.EnableL2SuggestedGasPricePolling')">RPC.EnableL2SuggestedGasPricePolling=</a> </div> <span class="badge badge-success default-value">Default: true</span><span class="badge badge-dark value-type">Type: boolean</span><br> <span class=description><p>EnableL2SuggestedGasPricePolling enables polling of the L2 gas price to block tx in the RPC with lower gas price.</p> </span> <hr> <div class=breadcrumbs> <!-- None --><!-- None --><a href=#RPC.TraceBatchUseHTTPS onclick="anchorLink('RPC.TraceBatchUseHTTPS')">RPC.TraceBatchUseHTTPS=</a> </div> <span class="badge badge-success default-value">Default: true</span><span class="badge badge-dark value-type">Type: boolean</span><br> <span class=description><p>TraceBatchUseHTTPS enables, in the debug<em>traceBatchByNum endpoint, the use of the HTTPS protocol (instead of HTTP)<br> to do the parallel requests to RPC.debug</em>traceTransaction endpoint</p> </span> <hr> </div> </div> </div> </div> <div class=accordion id=accordionSynchronizer> <div class=card> <div class=card-header id=headingSynchronizer> <h2 class=mb-0> <button class="btn btn-link property-name-button" type=button data-toggle=collapse data-target=#Synchronizer aria-expanded aria-controls=Synchronizer onclick="setAnchor('#Synchronizer')"><span class=property-name> <div class=breadcrumbs>[<a href=#Synchronizer onclick="anchorLink('Synchronizer')">Synchronizer</a>] </div></span></button> </h2> Configuration of service `Syncrhonizer`. For this service is also really important the value of `IsTrustedSequencer` because depending of this values is going to ask to a trusted node for trusted transactions or not </div> <div id=Synchronizer class="collapse property-definition-div" aria-labelledby=headingSynchronizer data-parent=#accordionSynchronizer> <div class="card-body pl-5"> <div class=breadcrumbs> <!-- None --><!-- None --><a href=#Synchronizer.SyncInterval onclick="anchorLink('Synchronizer.SyncInterval')">Synchronizer.SyncInterval=</a> </div> <span class="badge badge-success default-value">Default: "1s"</span><span class="badge badge-dark value-type">Type: string</span><br> <span class=description><p>SyncInterval is the delay interval between reading new rollup information</p> </span> <br> <div class="badge badge-secondary">Examples:</div> <br><div id=Synchronizer_SyncInterval_ex1 class="jumbotron examples"><div class=highlight><pre><span></span><span class=s2>&quot;1m&quot;</span>
+</pre></div> </div> <hr> <div class=breadcrumbs> <!-- None --><!-- None --><a href=#RPC.MaxRequestsPerIPAndSecond onclick="anchorLink('RPC.MaxRequestsPerIPAndSecond')">RPC.MaxRequestsPerIPAndSecond=</a> </div> <span class="badge badge-success default-value">Default: 500</span><span class="badge badge-dark value-type">Type: number</span><br> <span class=description><p>MaxRequestsPerIPAndSecond defines how much requests a single IP can<br> send within a single second</p> </span> <hr> <div class=breadcrumbs> <!-- None --><!-- None --><a href=#RPC.SequencerNodeURI onclick="anchorLink('RPC.SequencerNodeURI')">RPC.SequencerNodeURI=</a> </div> <span class="badge badge-success default-value">Default: ""</span><span class="badge badge-dark value-type">Type: string</span><br> <span class=description><p>SequencerNodeURI is used allow Non-Sequencer nodes<br> to relay transactions to the Sequencer node</p> </span> <hr> <div class=breadcrumbs> <!-- None --><!-- None --><a href=#RPC.MaxCumulativeGasUsed onclick="anchorLink('RPC.MaxCumulativeGasUsed')">RPC.MaxCumulativeGasUsed=</a> </div> <span class="badge badge-success default-value">Default: 0</span><span class="badge badge-dark value-type">Type: integer</span><br> <span class=description><p>MaxCumulativeGasUsed is the max gas allowed per batch</p> </span> <hr> <div class=accordion id=accordionRPC_WebSockets> <div class=card> <div class=card-header id=headingRPC_WebSockets> <h2 class=mb-0> <button class="btn btn-link property-name-button" type=button data-toggle=collapse data-target=#RPC_WebSockets aria-expanded aria-controls=RPC_WebSockets onclick="setAnchor('#RPC_WebSockets')"><span class=property-name> <div class=breadcrumbs>[<a href=#RPC onclick="anchorLink('RPC')">RPC</a> . <a href=#RPC_WebSockets onclick="anchorLink('RPC_WebSockets')">WebSockets</a>] </div></span></button> </h2> WebSockets configuration </div> <div id=RPC_WebSockets class="collapse property-definition-div" aria-labelledby=headingRPC_WebSockets data-parent=#accordionRPC_WebSockets> <div class="card-body pl-5"> <div class=breadcrumbs> <!-- None --><!-- None --><!-- None --><a href=#RPC.WebSockets.Enabled onclick="anchorLink('RPC.WebSockets.Enabled')">RPC.WebSockets.Enabled=</a> </div> <span class="badge badge-success default-value">Default: true</span><span class="badge badge-dark value-type">Type: boolean</span><br> <span class=description><p>Enabled defines if the WebSocket requests are enabled or disabled</p> </span> <hr> <div class=breadcrumbs> <!-- None --><!-- None --><!-- None --><a href=#RPC.WebSockets.Host onclick="anchorLink('RPC.WebSockets.Host')">RPC.WebSockets.Host=</a> </div> <span class="badge badge-success default-value">Default: "0.0.0.0"</span><span class="badge badge-dark value-type">Type: string</span><br> <span class=description><p>Host defines the network adapter that will be used to serve the WS requests</p> </span> <hr> <div class=breadcrumbs> <!-- None --><!-- None --><!-- None --><a href=#RPC.WebSockets.Port onclick="anchorLink('RPC.WebSockets.Port')">RPC.WebSockets.Port=</a> </div> <span class="badge badge-success default-value">Default: 8546</span><span class="badge badge-dark value-type">Type: integer</span><br> <span class=description><p>Port defines the port to serve the endpoints via WS</p> </span> <hr> <div class=breadcrumbs> <!-- None --><!-- None --><!-- None --><a href=#RPC.WebSockets.ReadLimit onclick="anchorLink('RPC.WebSockets.ReadLimit')">RPC.WebSockets.ReadLimit=</a> </div> <span class="badge badge-success default-value">Default: 104857600</span><span class="badge badge-dark value-type">Type: integer</span><br> <span class=description><p>ReadLimit defines the maximum size of a message read from the client (in bytes)</p> </span> <hr> </div> </div> </div> </div> <div class=breadcrumbs> <!-- None --><!-- None --><a href=#RPC.EnableL2SuggestedGasPricePolling onclick="anchorLink('RPC.EnableL2SuggestedGasPricePolling')">RPC.EnableL2SuggestedGasPricePolling=</a> </div> <span class="badge badge-success default-value">Default: true</span><span class="badge badge-dark value-type">Type: boolean</span><br> <span class=description><p>EnableL2SuggestedGasPricePolling enables polling of the L2 gas price to block tx in the RPC with lower gas price.</p> </span> <hr> <div class=breadcrumbs> <!-- None --><!-- None --><a href=#RPC.TraceBatchUseHTTPS onclick="anchorLink('RPC.TraceBatchUseHTTPS')">RPC.TraceBatchUseHTTPS=</a> </div> <span class="badge badge-success default-value">Default: true</span><span class="badge badge-dark value-type">Type: boolean</span><br> <span class=description><p>TraceBatchUseHTTPS enables, in the debug<em>traceBatchByNum endpoint, the use of the HTTPS protocol (instead of HTTP)<br> to do the parallel requests to RPC.debug</em>traceTransaction endpoint</p> </span> <hr> </div> </div> </div> </div> <div class=accordion id=accordionSynchronizer> <div class=card> <div class=card-header id=headingSynchronizer> <h2 class=mb-0> <button class="btn btn-link property-name-button" type=button data-toggle=collapse data-target=#Synchronizer aria-expanded aria-controls=Synchronizer onclick="setAnchor('#Synchronizer')"><span class=property-name> <div class=breadcrumbs>[<a href=#Synchronizer onclick="anchorLink('Synchronizer')">Synchronizer</a>] </div></span></button> </h2> Configuration of service `Syncrhonizer`. For this service is also really important the value of `IsTrustedSequencer` because depending of this values is going to ask to a trusted node for trusted transactions or not </div> <div id=Synchronizer class="collapse property-definition-div" aria-labelledby=headingSynchronizer data-parent=#accordionSynchronizer> <div class="card-body pl-5"> <div class=breadcrumbs> <!-- None --><!-- None --><a href=#Synchronizer.SyncInterval onclick="anchorLink('Synchronizer.SyncInterval')">Synchronizer.SyncInterval=</a> </div> <span class="badge badge-success default-value">Default: "1s"</span><span class="badge badge-dark value-type">Type: string</span><br> <span class=description><p>SyncInterval is the delay interval between reading new rollup information</p> </span> <br> <div class="badge badge-secondary">Examples:</div> <br><div id=Synchronizer_SyncInterval_ex1 class="jumbotron examples"><div class=highlight><pre><span></span><span class=s2>&quot;1m&quot;</span>
 </pre></div> </div><div id=Synchronizer_SyncInterval_ex2 class="jumbotron examples"><div class=highlight><pre><span></span><span class=s2>&quot;300ms&quot;</span>
 </pre></div> </div> <hr> <div class=breadcrumbs> <!-- None --><!-- None --><a href=#Synchronizer.SyncChunkSize onclick="anchorLink('Synchronizer.SyncChunkSize')">Synchronizer.SyncChunkSize=</a> </div> <span class="badge badge-success default-value">Default: 100</span><span class="badge badge-dark value-type">Type: integer</span><br> <span class=description><p>SyncChunkSize is the number of blocks to sync on each chunk</p> </span> <hr> <div class=breadcrumbs> <!-- None --><!-- None --><a href=#Synchronizer.TrustedSequencerURL onclick="anchorLink('Synchronizer.TrustedSequencerURL')">Synchronizer.TrustedSequencerURL=</a> </div> <span class="badge badge-success default-value">Default: ""</span><span class="badge badge-dark value-type">Type: string</span><br> <span class=description><p>TrustedSequencerURL is the rpc url to connect and sync the trusted state</p> </span> <hr> </div> </div> </div> </div> <div class=accordion id=accordionSequencer> <div class=card> <div class=card-header id=headingSequencer> <h2 class=mb-0> <button class="btn btn-link property-name-button" type=button data-toggle=collapse data-target=#Sequencer aria-expanded aria-controls=Sequencer onclick="setAnchor('#Sequencer')"><span class=property-name> <div class=breadcrumbs>[<a href=#Sequencer onclick="anchorLink('Sequencer')">Sequencer</a>] </div></span></button> </h2> Configuration of the sequencer service </div> <div id=Sequencer class="collapse property-definition-div" aria-labelledby=headingSequencer data-parent=#accordionSequencer> <div class="card-body pl-5"> <div class=breadcrumbs> <!-- None --><!-- None --><a href=#Sequencer.WaitPeriodPoolIsEmpty onclick="anchorLink('Sequencer.WaitPeriodPoolIsEmpty')">Sequencer.WaitPeriodPoolIsEmpty=</a> </div> <span class="badge badge-success default-value">Default: "1s"</span><span class="badge badge-dark value-type">Type: string</span><br> <span class=description><p>WaitPeriodPoolIsEmpty is the time the sequencer waits until<br> trying to add new txs to the state</p> </span> <br> <div class="badge badge-secondary">Examples:</div> <br><div id=Sequencer_WaitPeriodPoolIsEmpty_ex1 class="jumbotron examples"><div class=highlight><pre><span></span><span class=s2>&quot;1m&quot;</span>
 </pre></div> </div><div id=Sequencer_WaitPeriodPoolIsEmpty_ex2 class="jumbotron examples"><div class=highlight><pre><span></span><span class=s2>&quot;300ms&quot;</span>
```

### docs/config-file/node-config-doc.md
```diff
@@ -847,11 +847,12 @@ MaxCumulativeGasUsed=0
 **Type:** : `object`
 **Description:** WebSockets configuration
 
-| Property                              | Pattern | Type    | Deprecated | Definition | Title/Description                                                           |
-| ------------------------------------- | ------- | ------- | ---------- | ---------- | --------------------------------------------------------------------------- |
-| - [Enabled](#RPC_WebSockets_Enabled ) | No      | boolean | No         | -          | Enabled defines if the WebSocket requests are enabled or disabled           |
-| - [Host](#RPC_WebSockets_Host )       | No      | string  | No         | -          | Host defines the network adapter that will be used to serve the WS requests |
-| - [Port](#RPC_WebSockets_Port )       | No      | integer | No         | -          | Port defines the port to serve the endpoints via WS                         |
+| Property                                  | Pattern | Type    | Deprecated | Definition | Title/Description                                                               |
+| ----------------------------------------- | ------- | ------- | ---------- | ---------- | ------------------------------------------------------------------------------- |
+| - [Enabled](#RPC_WebSockets_Enabled )     | No      | boolean | No         | -          | Enabled defines if the WebSocket requests are enabled or disabled               |
+| - [Host](#RPC_WebSockets_Host )           | No      | string  | No         | -          | Host defines the network adapter that will be used to serve the WS requests     |
+| - [Port](#RPC_WebSockets_Port )           | No      | integer | No         | -          | Port defines the port to serve the endpoints via WS                             |
+| - [ReadLimit](#RPC_WebSockets_ReadLimit ) | No      | integer | No         | -          | ReadLimit defines the maximum size of a message read from the client (in bytes) |
 
 #### <a name="RPC_WebSockets_Enabled"></a>8.8.1. `RPC.WebSockets.Enabled`
 
@@ -895,6 +896,20 @@ Host="0.0.0.0"
 Port=8546
 ```
 
+#### <a name="RPC_WebSockets_ReadLimit"></a>8.8.4. `RPC.WebSockets.ReadLimit`
+
+**Type:** : `integer`
+
+**Default:** `104857600`
+
+**Description:** ReadLimit defines the maximum size of a message read from the client (in bytes)
+
+**Example setting the default value** (104857600):
+```
+[RPC.WebSockets]
+ReadLimit=104857600
+```
+
 ### <a name="RPC_EnableL2SuggestedGasPricePolling"></a>8.9. `RPC.EnableL2SuggestedGasPricePolling`
 
 **Type:** : `boolean`
```

### docs/config-file/node-config-schema.json
```diff
@@ -329,6 +329,11 @@
 							"type": "integer",
 							"description": "Port defines the port to serve the endpoints via WS",
 							"default": 8546
+						},
+						"ReadLimit": {
+							"type": "integer",
+							"description": "ReadLimit defines the maximum size of a message read from the client (in bytes)",
+							"default": 104857600
 						}
 					},
 					"additionalProperties": false,
```

### jsonrpc/config.go
```diff
@@ -50,4 +50,7 @@ type WebSocketsConfig struct {
 
 	// Port defines the port to serve the endpoints via WS
 	Port int `mapstructure:"Port"`
+
+	// ReadLimit defines the maximum size of a message read from the client (in bytes)
+	ReadLimit int64 `mapstructure:"ReadLimit"`
 }
```

### jsonrpc/server.go
```diff
@@ -337,6 +337,9 @@ func (s *Server) handleWs(w http.ResponseWriter, req *http.Request) {
 		return
 	}
 
+	// Set read limit
+	wsConn.SetReadLimit(s.config.WebSockets.ReadLimit)
+
 	// Defer WS closure
 	defer func(ws *websocket.Conn) {
 		err = ws.Close()
@@ -352,6 +355,8 @@ func (s *Server) handleWs(w http.ResponseWriter, req *http.Request) {
 		if err != nil {
 			if websocket.IsCloseError(err, websocket.CloseGoingAway, websocket.CloseNormalClosure, websocket.CloseAbnormalClosure) {
 				log.Info("Closing WS connection gracefully")
+			} else if errors.Is(err, websocket.ErrReadLimit) {
+				log.Info("Closing WS connection due to read limit exceeded")
 			} else {
 				log.Error(fmt.Sprintf("Unable to read WS message, %s", err.Error()))
 				log.Info("Closing WS connection with error")
```

### test/e2e/jsonrpc2_test.go
```diff
@@ -486,11 +486,11 @@ func TestWebSocketsConcurrentWrites(t *testing.T) {
 		log.Infof("Network %s", network.Name)
 
 		wsConn, _, err := websocket.DefaultDialer.Dial(network.WebSocketURL, nil)
+		require.NoError(t, err)
 		defer func() {
 			err := wsConn.Close()
 			require.NoError(t, err)
 		}()
-		require.NoError(t, err)
 
 		wg := sync.WaitGroup{}
 		wg.Add(msgQty)
@@ -527,6 +527,29 @@ func TestWebSocketsConcurrentWrites(t *testing.T) {
 	}
 }
 
+func TestWebSocketsReadLimit(t *testing.T) {
+	if testing.Short() {
+		t.Skip()
+	}
+	setup()
+	defer teardown()
+
+	wsConn, _, err := websocket.DefaultDialer.Dial(operations.DefaultL2NetworkWebSocketURL, nil)
+	require.NoError(t, err)
+	defer func() {
+		err := wsConn.Close()
+		require.NoError(t, err)
+	}()
+
+	jReq := make([]byte, 104857601)
+	err = wsConn.WriteMessage(websocket.TextMessage, jReq)
+	require.NoError(t, err)
+
+	_, _, err = wsConn.ReadMessage()
+	require.NotNil(t, err)
+	require.Equal(t, websocket.CloseMessageTooBig, err.(*websocket.CloseError).Code)
+}
+
 // waitTimeout waits for the waitgroup for the specified max timeout.
 // Returns true if waiting timed out.
 func waitTimeout(wg *sync.WaitGroup, timeout time.Duration) bool {
```
