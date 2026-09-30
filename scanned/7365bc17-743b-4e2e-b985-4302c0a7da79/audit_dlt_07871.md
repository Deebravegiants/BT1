# [?] VC: Fix VC must not crash if beacon node address could not be resolved. (#5388)

## Summary
Severity: Unknown
Chain: Ethereum
Component: status-im/nimbus-eth2
Published: 2023-09-15
Source: https://github.com/status-im/nimbus-eth2/commit/aec953e4da5dcdec6efc63551c2881351e22e210
Type: security-commit

## Details
VC: Fix VC must not crash if beacon node address could not be resolved. (#5388)

* Fix VC should not crash, if beacon node URL could not be resolved.

* Bump chronos.

* Update .gitmodules.

## Patch
### .gitmodules
```diff
@@ -59,7 +59,7 @@
 	path = vendor/nim-chronos
 	url = https://github.com/status-im/nim-chronos.git
 	ignore = untracked
-	branch = nimbus-v23.9.0
+	branch = master
 [submodule "vendor/nim-chronicles"]
 	path = vendor/nim-chronicles
 	url = https://github.com/status-im/nim-chronicles.git
```

### beacon_chain/nimbus_validator_client.nim
```diff
@@ -19,8 +19,21 @@ proc initGenesis(vc: ValidatorClientRef): Future[RestGenesis] {.async.} =
   var nodes = vc.beaconNodes
   while true:
     var pendingRequests: seq[Future[RestResponse[GetGenesisResponse]]]
-    for node in nodes:
-      debug "Requesting genesis information", endpoint = node
+    let offlineNodes = vc.offlineNodes()
+    if len(offlineNodes) == 0:
+      let sleepDuration = 2.seconds
+      info "Could not resolve beacon nodes, repeating",
+           sleep_time = sleepDuration
+      await sleepAsync(sleepDuration)
+      for node in vc.nonameNodes():
+        let status = checkName(node)
+        node.updateStatus(status, ApiNodeFailure())
+        if status == RestBeaconNodeStatus.Noname:
+          warn "Cannot initialize beacon node", node = node, status = status
+      continue
+
+    for node in offlineNodes:
+      debug "Requesting genesis information", node = node
       pendingRequests.add(node.client.getGenesis())
 
     try:
@@ -240,7 +253,8 @@ proc new*(T: type ValidatorClientRef,
           warn "Unable to initialize remote beacon node",
                 url = $url, error = res.error()
         else:
-          debug "Beacon node was initialized", node = res.get()
+          if res.get().status != RestBeaconNodeStatus.Noname:
+            debug "Beacon node was initialized", node = res.get()
           servers.add(res.get())
       let missingRoles = getMissingRoles(servers)
       if len(missingRoles) != 0:
@@ -296,7 +310,10 @@ proc asyncInit(vc: ValidatorClientRef): Future[ValidatorClientRef] {.async.} =
                                        beacon_nodes_count = len(vc.beaconNodes)
 
   for node in vc.beaconNodes:
-    notice "Beacon node initialized", node = node
+    if node.status == RestBeaconNodeStatus.Offline:
+      notice "Beacon node initialized", node = node
+    else:
+      notice "Cannot initialize beacon node", node = node, status = node.status
 
   vc.beaconGenesis = await vc.initGenesis()
   info "Genesis information", genesis_time = vc.beaconGenesis.genesis_time,
```

### beacon_chain/validator_client/block_service.nim
```diff
@@ -734,7 +734,7 @@ proc runBlockPollMonitor(service: BlockServiceRef,
 proc runBlockMonitor(service: BlockServiceRef) {.async.} =
   let
     vc = service.client
-    blockNodes = vc.filterNodes(AllBeaconNodeStatuses,
+    blockNodes = vc.filterNodes(ResolvedBeaconNodeStatuses,
                                 {BeaconNodeRole.BlockProposalData})
   let pendingTasks =
     case vc.config.monitoringType
```

### beacon_chain/validator_client/common.nim
```diff
@@ -118,6 +118,7 @@ type
 
   BeaconNodeServer* = object
     client*: RestClientRef
+    uri*: Uri
     endpoint*: string
     config*: VCRuntimeConfig
     ident*: Opt[string]
@@ -146,6 +147,8 @@ type
     proofs*: Table[ValidatorPubKey, SyncCommitteeSelectionProof]
 
   RestBeaconNodeStatus* {.pure.} = enum
+    Invalid,            ## BN address is invalid.
+    Noname,             ## BN address could not be resolved yet.
     Offline,            ## BN is offline.
     Online,             ## BN is online, passed checkOnline() check.
     Incompatible,       ## BN configuration is NOT compatible with VC.
@@ -284,6 +287,22 @@ const
     ## are enabled by default.
 
   AllBeaconNodeStatuses* = {
+    RestBeaconNodeStatus.Invalid,
+    RestBeaconNodeStatus.Noname,
+    RestBeaconNodeStatus.Offline,
+    RestBeaconNodeStatus.Online,
+    RestBeaconNodeStatus.Incompatible,
+    RestBeaconNodeStatus.Compatible,
+    RestBeaconNodeStatus.NotSynced,
+    RestBeaconNodeStatus.OptSynced,
+    RestBeaconNodeStatus.Synced,
+    RestBeaconNodeStatus.UnexpectedCode,
+    RestBeaconNodeStatus.UnexpectedResponse,
+    RestBeaconNodeStatus.BrokenClock,
+    RestBeaconNodeStatus.InternalError
+  }
+
+  ResolvedBeaconNodeStatuses* = {
     RestBeaconNodeStatus.Offline,
     RestBeaconNodeStatus.Online,
     RestBeaconNodeStatus.Incompatible,
@@ -341,6 +360,8 @@ proc `$`*(roles: set[BeaconNodeRole]): string =
 
 proc `$`*(status: RestBeaconNodeStatus): string =
   case status
+  of RestBeaconNodeStatus.Invalid: "invalid-address"
+  of RestBeaconNodeStatus.Noname: "dns-error"
   of RestBeaconNodeStatus.Offline: "offline"
   of RestBeaconNodeStatus.Online: "online"
   of RestBeaconNodeStatus.Incompatible: "incompatible"
@@ -548,11 +569,23 @@ proc updateStatus*(node: BeaconNodeServerRef,
     node = node
 
   case status
-  of RestBeaconNodeStatus.Offline:
+  of RestBeaconNodeStatus.Invalid:
     if node.status != status:
-      warn "Beacon node down",
-           reason = failure.getFailureReason()
+      warn "Beacon node could not be used"
       node.status = status
+  of RestBeaconNodeStatus.Noname:
+    if node.status != status:
+      warn "Beacon node address cannot be resolved"
+      node.status = status
+  of RestBeaconNodeStatus.Offline:
+    if node.status != status:
+      if node.status in {RestBeaconNodeStatus.Invalid,
+                         RestBeaconNodeStatus.Noname}:
+        notice "Beacon node address has been resolved"
+        node.status = status
+      else:
+        warn "Beacon node down", reason = failure.getFailureReason()
+        node.status = status
   of RestBeaconNodeStatus.Online:
     if node.status != status:
       let version = if node.ident.isSome(): node.ident.get() else: "<missing>"
@@ -717,25 +750,38 @@ proc normalizeUri*(r: Uri): Result[Uri, cstring] =
 
   ok(normalized)
 
+proc initClient*(uri: Uri): Result[RestClientRef, HttpAddressErrorType] =
+  let
+    flags = {RestClientFlag.CommaSeparatedArray}
+    socketFlags = {SocketFlags.TcpNoDelay}
+    address = ? getHttpAddress(uri)
+    client = RestClientRef.new(address, flags = flags,
+                               socketFlags = socketFlags)
+  ok(client)
+
 proc init*(t: typedesc[BeaconNodeServerRef], remote: Uri,
            index: int): Result[BeaconNodeServerRef, string] =
   doAssert(index >= 0)
   let
-    flags = {RestClientFlag.CommaSeparatedArray}
-    socketFlags = {SocketFlags.TcpNoDelay}
     remoteUri = normalizeUri(remote).valueOr:
       return err($error)
-    client = RestClientRef.new($remoteUri, flags = flags,
-                               socketFlags = socketFlags).valueOr:
-      return err($error)
     roles = parseRoles(remoteUri.anchor).valueOr:
       return err($error)
-
-  let server = BeaconNodeServerRef(
-    client: client, endpoint: $remoteUri, index: index, roles: roles,
-    logIdent: $client.address.getUri(),
-    status: RestBeaconNodeStatus.Offline
-  )
+    server =
+      block:
+        let res = initClient(remoteUri)
+        if res.isOk():
+          BeaconNodeServerRef(
+            client: res.get(), endpoint: $remoteUri, index: index,
+            roles: roles, logIdent: $(res.get().address.getUri()),
+            uri: remoteUri, status: RestBeaconNodeStatus.Offline)
+        else:
+          if res.error.isCriticalError():
+            return err(res.error.toString())
+          BeaconNodeServerRef(
+            client: nil, endpoint: $remoteUri, index: index,
+            roles: roles, logIdent: $remoteUri, uri: remoteUri,
+            status: RestBeaconNodeStatus.Noname)
   ok(server)
 
 proc getMissingRoles*(n: openArray[BeaconNodeServerRef]): set[BeaconNodeRole] =
```

### beacon_chain/validator_client/fallback_service.nim
```diff
@@ -45,6 +45,12 @@ proc filterNodes*(vc: ValidatorClientRef, statuses: set[RestBeaconNodeStatus],
     vc.beaconNodes.filterIt((it.roles * roles != {}) and
                             (it.status in statuses))
 
+proc nonameNodes*(vc: ValidatorClientRef): seq[BeaconNodeServerRef] =
+  vc.beaconNodes.filterIt(it.status == RestBeaconNodeStatus.Noname)
+
+proc offlineNodes*(vc: ValidatorClientRef): seq[BeaconNodeServerRef] =
+  vc.beaconNodes.filterIt(it.status == RestBeaconNodeStatus.Offline)
+
 proc otherNodes*(vc: ValidatorClientRef): seq[BeaconNodeServerRef] =
   vc.beaconNodes.filterIt(it.status != RestBeaconNodeStatus.Synced)
 
@@ -91,6 +97,25 @@ proc waitNodes*(vc: ValidatorClientRef, timeoutFut: Future[void],
 
     inc(iterations)
 
+proc checkName*(
+       node: BeaconNodeServerRef): RestBeaconNodeStatus {.raises: [].} =
+  ## Could return only {Invalid, Noname, Offline}
+  logScope: endpoint = node
+  let client =
+    block:
+      let res = initClient(node.uri)
+      if res.isErr():
+        return
+          case res.error
+          of CriticalHttpAddressError:
+            RestBeaconNodeStatus.Invalid
+          of RecoverableHttpAddressError:
+            RestBeaconNodeStatus.Noname
+      res.get()
+
+  node.client = client
+  RestBeaconNodeStatus.Offline
+
 proc checkCompatible(
        vc: ValidatorClientRef,
        node: BeaconNodeServerRef
@@ -225,6 +250,10 @@ proc checkOnline(
 
 func getReason(status: RestBeaconNodeStatus): string =
   case status
+  of RestBeaconNodeStatus.Invalid:
+    "Beacon node address invalid"
+  of RestBeaconNodeStatus.Noname:
+    "Beacon node address cannot be resolved"
   of RestBeaconNodeStatus.Offline:
     "Connection with node has been lost"
   of RestBeaconNodeStatus.Online:
@@ -237,6 +266,15 @@ proc checkNode(vc: ValidatorClientRef,
   let nstatus = node.status
   debug "Checking beacon node", endpoint = node, status = node.status
 
+  if nstatus in {RestBeaconNodeStatus.Noname}:
+    let
+      status = node.checkName()
+      failure = ApiNodeFailure.init(ApiFailure.NoError, "checkName",
+                                    node, status.getReason())
+    node.updateStatus(status, failure)
+    if status != RestBeaconNodeStatus.Offline:
+      return nstatus != status
+
   if nstatus in {RestBeaconNodeStatus.Offline,
                  RestBeaconNodeStatus.UnexpectedCode,
                  RestBeaconNodeStatus.UnexpectedResponse,
@@ -408,7 +446,8 @@ proc runTimeMonitor(service: FallbackServiceRef,
 proc processTimeMonitoring(service: FallbackServiceRef) {.async.} =
   let
     vc = service.client
-    blockNodes = vc.filterNodes(AllBeaconNodeStatuses, AllBeaconNodeRoles)
+    blockNodes = vc.filterNodes(
+      ResolvedBeaconNodeStatuses, AllBeaconNodeRoles)
 
   var pendingChecks: seq[Future[void]]
 
```

### vendor/nim-chronos
```diff
@@ -1 +1 @@
-Subproject commit 176d462b076db24d9f71ddb40163d1ef82823771
+Subproject commit 00614476c68f0553432b4bb505e24d6ad5586ae4
```

### vendor/nim-presto
```diff
@@ -1 +1 @@
-Subproject commit 8bb4a54f4751dc560efc24003be4b3b2b28316e7
+Subproject commit cb9353acd5877f7ba197bfe1f365b89a0a4473f8
```
