# [?] fix nil pointer panic on version strings in ID message

## Summary
Severity: Unknown
Chain: libp2p
Component: libp2p/go-libp2p
Published: 2015-01-29
Source: https://github.com/libp2p/go-libp2p/commit/704625bceb80df91161b842c8d684f5d330227b7
Type: security-commit

## Details
fix nil pointer panic on version strings in ID message

## Patch
### protocol/identify/id.go
```diff
@@ -180,8 +180,8 @@ func (ids *IDService) consumeMessage(mes *pb.Identify, c inet.Conn) {
 	log.Debugf("%s received listen addrs for %s: %s", c.LocalPeer(), c.RemotePeer(), lmaddrs)
 
 	// get protocol versions
-	pv := *mes.ProtocolVersion
-	av := *mes.AgentVersion
+	pv := mes.GetProtocolVersion()
+	av := mes.GetAgentVersion()
 	ids.Host.Peerstore().Put(p, "ProtocolVersion", pv)
 	ids.Host.Peerstore().Put(p, "AgentVersion", av)
 }
```
