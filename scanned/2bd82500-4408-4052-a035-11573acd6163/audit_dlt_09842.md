# [?] fix concurrent map access crash in node sync

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2019-06-25
Source: https://github.com/harmony-one/harmony/commit/5d107f53fbd6a3c9f92d6c7e4d13879f0a523111
Type: security-commit

## Details
fix concurrent map access crash in node sync

## Patch
### node/node_syncing.go
```diff
@@ -197,26 +197,22 @@ func (node *Node) SendNewBlockToUnsync() {
 			continue
 		}
 
+		node.stateMutex.Lock()
 		for peerID, config := range node.peerRegistrationRecord {
 			elapseTime := time.Now().UnixNano() - config.timestamp
 			if elapseTime > broadcastTimeout {
 				utils.GetLogInstance().Warn("[SYNC] SendNewBlockToUnsync to peer timeout", "peerID", peerID)
-				// send last time and delete
-				config.client.PushNewBlock(node.GetSyncID(), blockHash, true)
-				node.stateMutex.Lock()
 				node.peerRegistrationRecord[peerID].client.Close()
 				delete(node.peerRegistrationRecord, peerID)
-				node.stateMutex.Unlock()
 				continue
 			}
 			response := config.client.PushNewBlock(node.GetSyncID(), blockHash, false)
 			if response != nil && response.Type == downloader_pb.DownloaderResponse_INSYNC {
-				node.stateMutex.Lock()
 				node.peerRegistrationRecord[peerID].client.Close()
 				delete(node.peerRegistrationRecord, peerID)
-				node.stateMutex.Unlock()
 			}
 		}
+		node.stateMutex.Unlock()
 	}
 }
 
@@ -290,6 +286,8 @@ func (node *Node) CalculateResponse(request *downloader_pb.DownloaderRequest) (*
 		peerID := string(request.PeerHash[:])
 		ip := request.Ip
 		port := request.Port
+		node.stateMutex.Lock()
+		defer node.stateMutex.Unlock()
 		if _, ok := node.peerRegistrationRecord[peerID]; ok {
 			response.Type = downloader_pb.DownloaderResponse_FAIL
 			utils.GetLogInstance().Warn("[SYNC] peerRegistration record already exists", "ip", ip, "port", port)
@@ -307,9 +305,7 @@ func (node *Node) CalculateResponse(request *downloader_pb.DownloaderRequest) (*
 				return response, nil
 			}
 			config := &syncConfig{timestamp: time.Now().UnixNano(), client: client}
-			node.stateMutex.Lock()
 			node.peerRegistrationRecord[peerID] = config
-			node.stateMutex.Unlock()
 			utils.GetLogInstance().Debug("[SYNC] register peerID success", "ip", ip, "port", port)
 			response.Type = downloader_pb.DownloaderResponse_SUCCESS
 		}
```
