# [?] Fix issue when VC crashes on invalid `beacon-node` argument. (#4765)

## Summary
Severity: Unknown
Chain: Ethereum
Component: status-im/nimbus-eth2
Published: 2023-04-03
Source: https://github.com/status-im/nimbus-eth2/commit/e2bf58a6f27d8851650939c4341e5fee00671a5e
Type: security-commit

## Details
Fix issue when VC crashes on invalid `beacon-node` argument. (#4765)

Make `beacon-node` URL argument less strict and more UX friendly.

## Patch
### beacon_chain/nimbus_validator_client.nim
```diff
@@ -205,19 +205,19 @@ proc new*(T: type ValidatorClientRef,
                 url = $url, error = res.error()
         else:
           debug "Beacon node was initialized", node = res.get()
-        servers.add(res.get())
+          servers.add(res.get())
       let missingRoles = getMissingRoles(servers)
       if len(missingRoles) != 0:
-        fatal "Beacon nodes do not use all required roles",
-              missing_roles = $missingRoles, nodes_count = len(servers)
-        quit 1
+        if len(servers) == 0:
+          fatal "Not enough beacon nodes available",
+                nodes_count = len(servers)
+          quit 1
+        else:
+          fatal "Beacon nodes do not cover all required roles",
+                missing_roles = $missingRoles, nodes_count = len(servers)
+          quit 1
       servers
 
-  if len(beaconNodes) == 0:
-    # This should not happen, thanks to defaults in `conf.nim`
-    fatal "Not enough beacon nodes in command line"
-    quit 1
-
   when declared(waitSignal):
     ValidatorClientRef(
       rng: rng,
@@ -255,6 +255,9 @@ proc asyncInit(vc: ValidatorClientRef): Future[ValidatorClientRef] {.async.} =
                                        config = vc.config,
                                        beacon_nodes_count = len(vc.beaconNodes)
 
+  for node in vc.beaconNodes:
+    notice "Beacon node initialized", node = node
+
   vc.beaconGenesis = await vc.initGenesis()
   info "Genesis information", genesis_time = vc.beaconGenesis.genesis_time,
     genesis_fork_version = vc.beaconGenesis.genesis_fork_version,
```

### beacon_chain/validator_client/common.nim
```diff
@@ -492,26 +492,58 @@ proc parseRoles*(data: string): Result[set[BeaconNodeRole], cstring] =
       return err("Invalid beacon node role string found")
   ok(res)
 
+proc normalizeUri*(remoteUri: Uri): Uri =
+  var r = remoteUri
+  if (len(r.scheme) == 0) and (len(r.username) == 0) and
+     (len(r.password) == 0) and (len(r.hostname) == 0) and
+     (len(r.port) == 0) and (len(r.path) > 0):
+    # When `scheme` is not specified and `port` is not specified - whole
+    # hostname is stored in `path`.`query` and `anchor` could still be present.
+    # test.com
+    # test.com?q=query
+    # test.com?q=query#anchor=anchor
+    parseUri("http://" & $remoteUri & ":" & $defaultEth2RestPort)
+  elif (len(r.scheme) > 0) and (len(r.username) == 0) and
+       (len(r.password) == 0) and (len(r.hostname) == 0) and
+       (len(r.port) == 0) and (len(r.path) > 0):
+    # When `scheme` is not specified but `port` is specified - whole
+    # hostname is stored in `scheme` and `port` is in `path`.
+    # 192.168.0.1:5052
+    # test.com:5052
+    # test.com:5052?q=query
+    # test.com:5052?q=query#anchor=anchor
+    parseUri("http://" & $remoteUri)
+  elif (len(r.scheme) > 0) and (len(r.hostname) > 0):
+    # When `scheme` is specified, but `port` is not we use default.
+    # http://192.168.0.1
+    # http://test.com
+    # http://test.com?q=query
+    # http://test.com?q=query#anchor=anchor
+    if len(r.port) == 0: r.port = $defaultEth2RestPort
+    r
+  else:
+    remoteUri
+
 proc init*(t: typedesc[BeaconNodeServerRef], remote: Uri,
            index: int): Result[BeaconNodeServerRef, string] =
   doAssert(index >= 0)
   let
     flags = {RestClientFlag.CommaSeparatedArray}
+    remoteUri = normalizeUri(remote)
     client =
       block:
-        let res = RestClientRef.new($remote, flags = flags)
+        let res = RestClientRef.new($remoteUri, flags = flags)
         if res.isErr(): return err($res.error())
         res.get()
     roles =
       block:
-        let res = parseRoles(remote.anchor)
+        let res = parseRoles(remoteUri.anchor)
         if res.isErr(): return err($res.error())
         res.get()
 
   let server = BeaconNodeServerRef(
-    client: client, endpoint: $remote, index: index, roles: roles,
-    logIdent: client.address.hostname & ":" &
-              Base10.toString(client.address.port),
+    client: client, endpoint: $remoteUri, index: index, roles: roles,
+    logIdent: $client.address.getUri(),
     status: RestBeaconNodeStatus.Offline
   )
   ok(server)
```
