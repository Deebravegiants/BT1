# [?] fix bootnode nil host panics in API methods

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2026-02-12
Source: https://github.com/harmony-one/harmony/commit/a2c0f5f9ca1ca9d34ceb01f89bd4a4e905090faa
Type: security-commit

## Details
fix bootnode nil host panics in API methods

## Patch
### node/boot/api.go
```diff
@@ -1,6 +1,7 @@
 package bootnode
 
 import (
+	"errors"
 	"time"
 
 	"github.com/harmony-one/harmony/eth/rpc"
@@ -14,18 +15,29 @@ import (
 	"github.com/libp2p/go-libp2p/core/peer"
 )
 
+var errHostNil = errors.New("bootnode host is nil")
+
 // PeerID returns self Peer ID
 func (bootnode *BootNode) PeerID() peer.ID {
+	if bootnode.host == nil {
+		return ""
+	}
 	return bootnode.host.GetID()
 }
 
 // PeerConnectivity ..
 func (bootnode *BootNode) PeerConnectivity() (int, int, int) {
+	if bootnode.host == nil {
+		return 0, 0, 0
+	}
 	return bootnode.host.PeerConnectivity()
 }
 
 // ListKnownPeers return known peers
 func (bootnode *BootNode) ListKnownPeers() peer.IDSlice {
+	if bootnode.host == nil {
+		return peer.IDSlice{}
+	}
 	bs := bootnode.host.GetP2PHost().Peerstore()
 	if bs == nil {
 		return peer.IDSlice{}
@@ -35,21 +47,33 @@ func (bootnode *BootNode) ListKnownPeers() peer.IDSlice {
 
 // ListConnectedPeers return connected peers
 func (bootnode *BootNode) ListConnectedPeers() []peer.ID {
+	if bootnode.host == nil {
+		return nil
+	}
 	return bootnode.host.Network().Peers()
 }
 
 // ListPeer return list of peers for a certain topic
 func (bootnode *BootNode) ListPeer(topic string) []peer.ID {
+	if bootnode.host == nil {
+		return nil
+	}
 	return bootnode.host.ListPeer(topic)
 }
 
 // ListTopic return list of topics the node subscribed
 func (bootnode *BootNode) ListTopic() []string {
+	if bootnode.host == nil {
+		return nil
+	}
 	return bootnode.host.ListTopic()
 }
 
 // ListBlockedPeer return list of blocked peers
 func (bootnode *BootNode) ListBlockedPeer() []peer.ID {
+	if bootnode.host == nil {
+		return nil
+	}
 	return bootnode.host.ListBlockedPeer()
 }
 
@@ -60,13 +84,20 @@ func (bootnode *BootNode) GetNodeBootTime() int64 {
 
 // StartRPC start RPC service
 func (bootnode *BootNode) StartRPC() error {
+	if bootnode.host == nil {
+		return errHostNil
+	}
+	if bootnode.RPCConfig == nil {
+		return errors.New("bootnode RPC config is nil")
+	}
+	if bootnode.HarmonyConfig == nil {
+		return errors.New("bootnode harmony config is nil")
+	}
 	bootService := hmy_boot.New(bootnode)
 	// Gather all the possible APIs to surface
 	apis := bootnode.APIs(bootService)
 
-	err := boot_rpc.StartServers(bootService, apis, *bootnode.RPCConfig, bootnode.HarmonyConfig.RPCOpt)
-
-	return err
+	return boot_rpc.StartServers(bootService, apis, *bootnode.RPCConfig, bootnode.HarmonyConfig.RPCOpt)
 }
 
 func (bootnode *BootNode) initRPCServerConfig() {
@@ -130,9 +161,14 @@ func (bootnode *BootNode) APIs(harmony *hmy_boot.BootService) []rpc.API {
 }
 
 func (bootnode *BootNode) GetConfig() rpc_common.Config {
-	return rpc_common.Config{
-		HarmonyConfig: *bootnode.HarmonyConfig,
-		NodeConfig:    *bootnode.NodeConfig,
-		ChainConfig:   params.ChainConfig{},
+	cfg := rpc_common.Config{
+		ChainConfig: params.ChainConfig{},
+	}
+	if bootnode.HarmonyConfig != nil {
+		cfg.HarmonyConfig = *bootnode.HarmonyConfig
+	}
+	if bootnode.NodeConfig != nil {
+		cfg.NodeConfig = *bootnode.NodeConfig
 	}
+	return cfg
 }
```
