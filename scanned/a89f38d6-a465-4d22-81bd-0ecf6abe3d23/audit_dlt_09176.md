# [?] fix: add NullResourceManager to webrtc, fixes panic (#2752)

## Summary
Severity: Unknown
Chain: libp2p
Component: libp2p/go-libp2p
Published: 2024-03-25
Source: https://github.com/libp2p/go-libp2p/commit/9854f25cefb244790b716849f7079be152f1923f
Type: security-commit

## Details
fix: add NullResourceManager to webrtc, fixes panic (#2752)

## Patch
### p2p/transport/webrtc/transport.go
```diff
@@ -113,6 +113,9 @@ func New(privKey ic.PrivKey, psk pnet.PSK, gater connmgr.ConnectionGater, rcmgr
 		log.Error("WebRTC doesn't support private networks yet.")
 		return nil, fmt.Errorf("WebRTC doesn't support private networks yet")
 	}
+	if rcmgr == nil {
+		rcmgr = &network.NullResourceManager{}
+	}
 	localPeerID, err := peer.IDFromPrivateKey(privKey)
 	if err != nil {
 		return nil, fmt.Errorf("get local peer ID: %w", err)
```
