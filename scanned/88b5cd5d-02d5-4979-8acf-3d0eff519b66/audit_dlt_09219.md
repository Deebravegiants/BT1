# [?] fix: deadlock on retrieving WebTransport addresses (#9857)

## Summary
Severity: Unknown
Chain: IPFS
Component: ipfs/kubo
Published: 2023-05-08
Source: https://github.com/ipfs/kubo/commit/8684f05ef376f5971b8df6f67e9aaddccdba5bed
Type: security-commit

## Details
fix: deadlock on retrieving WebTransport addresses (#9857)

Co-authored-by: Marco Polo <git@marcopolo.io>

## Patch
### core/mock/mock.go
```diff
@@ -34,7 +34,16 @@ func NewMockNode() (*core.IpfsNode, error) {
 }
 
 func MockHostOption(mn mocknet.Mocknet) libp2p2.HostOption {
-	return func(id peer.ID, ps pstore.Peerstore, _ ...libp2p.Option) (host.Host, error) {
+	return func(id peer.ID, ps pstore.Peerstore, opts ...libp2p.Option) (host.Host, error) {
+		var cfg libp2p.Config
+		if err := cfg.Apply(opts...); err != nil {
+			return nil, err
+		}
+
+		// The mocknet does not use the provided libp2p.Option. This options include
+		// the listening addresses we want our peer listening on. Therefore, we have
+		// to manually parse the configuration and add them here.
+		ps.AddAddrs(id, cfg.ListenAddrs, pstore.PermanentAddrTTL)
 		return mn.AddPeerWithPeerstore(id, ps)
 	}
 }
```

### core/node/groups.go
```diff
@@ -155,7 +155,7 @@ func LibP2P(bcfg *BuildCfg, cfg *config.Config, userResourceOverrides rcmgr.Part
 		fx.Provide(libp2p.RelayTransport(enableRelayTransport)),
 		fx.Provide(libp2p.RelayService(enableRelayService, cfg.Swarm.RelayService)),
 		fx.Provide(libp2p.Transports(cfg.Swarm.Transports)),
-		fx.Invoke(libp2p.StartListening(cfg.Addresses.Swarm)),
+		fx.Provide(libp2p.ListenOn(cfg.Addresses.Swarm)),
 		fx.Invoke(libp2p.SetupDiscovery(cfg.Discovery.MDNS.Enabled)),
 		fx.Provide(libp2p.ForceReachability(cfg.Internal.Libp2pForceReachability)),
 		fx.Provide(libp2p.HolePunching(cfg.Swarm.EnableHolePunching, enableRelayClient)),
```

### core/node/libp2p/addrs.go
```diff
@@ -4,7 +4,6 @@ import (
 	"fmt"
 
 	"github.com/libp2p/go-libp2p"
-	"github.com/libp2p/go-libp2p/core/host"
 	p2pbhost "github.com/libp2p/go-libp2p/p2p/host/basic"
 	ma "github.com/multiformats/go-multiaddr"
 	mamask "github.com/whyrusleeping/multiaddr-filter"
@@ -99,37 +98,12 @@ func AddrsFactory(announce []string, appendAnnouce []string, noAnnounce []string
 	}
 }
 
-func listenAddresses(addresses []string) ([]ma.Multiaddr, error) {
-	listen := make([]ma.Multiaddr, len(addresses))
-	for i, addr := range addresses {
-		maddr, err := ma.NewMultiaddr(addr)
-		if err != nil {
-			return nil, fmt.Errorf("failure to parse config.Addresses.Swarm: %s", addresses)
-		}
-		listen[i] = maddr
-	}
-
-	return listen, nil
-}
-
-func StartListening(addresses []string) func(host host.Host) error {
-	return func(host host.Host) error {
-		listenAddrs, err := listenAddresses(addresses)
-		if err != nil {
-			return err
-		}
-
-		// Actually start listening:
-		if err := host.Network().Listen(listenAddrs...); err != nil {
-			return err
-		}
-
-		// list out our addresses
-		addrs, err := host.Network().InterfaceListenAddresses()
-		if err != nil {
-			return err
+func ListenOn(addresses []string) interface{} {
+	return func() (opts Libp2pOpts) {
+		return Libp2pOpts{
+			Opts: []libp2p.Option{
+				libp2p.ListenAddrStrings(addresses...),
+			},
 		}
-		log.Infof("Swarm listening at: %s", addrs)
-		return nil
 	}
 }
```

### docs/examples/kubo-as-a-library/go.mod
```diff
@@ -9,7 +9,7 @@ replace github.com/ipfs/kubo => ./../../..
 require (
 	github.com/ipfs/boxo v0.8.1
 	github.com/ipfs/kubo v0.0.0-00010101000000-000000000000
-	github.com/libp2p/go-libp2p v0.27.1
+	github.com/libp2p/go-libp2p v0.27.2
 	github.com/multiformats/go-multiaddr v0.9.0
 )
 
```

### docs/examples/kubo-as-a-library/go.sum
```diff
@@ -489,8 +489,8 @@ github.com/libp2p/go-flow-metrics v0.0.1/go.mod h1:Iv1GH0sG8DtYN3SVJ2eG221wMiNpZ
 github.com/libp2p/go-flow-metrics v0.0.3/go.mod h1:HeoSNUrOJVK1jEpDqVEiUOIXqhbnS27omG0uWU5slZs=
 github.com/libp2p/go-flow-metrics v0.1.0 h1:0iPhMI8PskQwzh57jB9WxIuIOQ0r+15PChFGkx3Q3WM=
 github.com/libp2p/go-flow-metrics v0.1.0/go.mod h1:4Xi8MX8wj5aWNDAZttg6UPmc0ZrnFNsMtpsYUClFtro=
-github.com/libp2p/go-libp2p v0.27.1 h1:k1u6RHsX3hqKnslDjsSgLNURxJ3O1atIZCY4gpMbbus=
-github.com/libp2p/go-libp2p v0.27.1/go.mod h1:FAvvfQa/YOShUYdiSS03IR9OXzkcJXwcNA2FUCh9ImE=
+github.com/libp2p/go-libp2p v0.27.2 h1:I1fxqxdm/O0TFoAZKje8wSMu9tfLlLdzTQvgT3HA6v0=
+github.com/libp2p/go-libp2p v0.27.2/go.mod h1:FAvvfQa/YOShUYdiSS03IR9OXzkcJXwcNA2FUCh9ImE=
 github.com/libp2p/go-libp2p-asn-util v0.3.0 h1:gMDcMyYiZKkocGXDQ5nsUQyquC9+H+iLEQHwOCZ7s8s=
 github.com/libp2p/go-libp2p-asn-util v0.3.0/go.mod h1:B1mcOrKUE35Xq/ASTmQ4tN3LNzVVaMNmq2NACuqyB9w=
 github.com/libp2p/go-libp2p-core v0.2.4/go.mod h1:STh4fdfa5vDYr0/SzYYeqnt+E6KfEV5VxfIrm0bcI0g=
```

### go.mod
```diff
@@ -45,7 +45,7 @@ require (
 	github.com/jbenet/goprocess v0.1.4
 	github.com/julienschmidt/httprouter v1.3.0
 	github.com/libp2p/go-doh-resolver v0.4.0
-	github.com/libp2p/go-libp2p v0.27.1
+	github.com/libp2p/go-libp2p v0.27.2
 	github.com/libp2p/go-libp2p-http v0.5.0
 	github.com/libp2p/go-libp2p-kad-dht v0.23.0
 	github.com/libp2p/go-libp2p-kbucket v0.5.0
```

### go.sum
```diff
@@ -540,8 +540,8 @@ github.com/libp2p/go-flow-metrics v0.0.1/go.mod h1:Iv1GH0sG8DtYN3SVJ2eG221wMiNpZ
 github.com/libp2p/go-flow-metrics v0.0.3/go.mod h1:HeoSNUrOJVK1jEpDqVEiUOIXqhbnS27omG0uWU5slZs=
 github.com/libp2p/go-flow-metrics v0.1.0 h1:0iPhMI8PskQwzh57jB9WxIuIOQ0r+15PChFGkx3Q3WM=
 github.com/libp2p/go-flow-metrics v0.1.0/go.mod h1:4Xi8MX8wj5aWNDAZttg6UPmc0ZrnFNsMtpsYUClFtro=
-github.com/libp2p/go-libp2p v0.27.1 h1:k1u6RHsX3hqKnslDjsSgLNURxJ3O1atIZCY4gpMbbus=
-github.com/libp2p/go-libp2p v0.27.1/go.mod h1:FAvvfQa/YOShUYdiSS03IR9OXzkcJXwcNA2FUCh9ImE=
+github.com/libp2p/go-libp2p v0.27.2 h1:I1fxqxdm/O0TFoAZKje8wSMu9tfLlLdzTQvgT3HA6v0=
+github.com/libp2p/go-libp2p v0.27.2/go.mod h1:FAvvfQa/YOShUYdiSS03IR9OXzkcJXwcNA2FUCh9ImE=
 github.com/libp2p/go-libp2p-asn-util v0.3.0 h1:gMDcMyYiZKkocGXDQ5nsUQyquC9+H+iLEQHwOCZ7s8s=
 github.com/libp2p/go-libp2p-asn-util v0.3.0/go.mod h1:B1mcOrKUE35Xq/ASTmQ4tN3LNzVVaMNmq2NACuqyB9w=
 github.com/libp2p/go-libp2p-core v0.2.4/go.mod h1:STh4fdfa5vDYr0/SzYYeqnt+E6KfEV5VxfIrm0bcI0g=
```

### test/cli/harness/peering.go
```diff
@@ -13,7 +13,7 @@ type Peering struct {
 	To   int
 }
 
-func newRandPort() int {
+func NewRandPort() int {
 	n := rand.Int()
 	return 3000 + (n % 1000)
 }
@@ -24,7 +24,7 @@ func CreatePeerNodes(t *testing.T, n int, peerings []Peering) (*Harness, Nodes)
 	nodes.ForEachPar(func(node *Node) {
 		node.UpdateConfig(func(cfg *config.Config) {
 			cfg.Routing.Type = config.NewOptionalString("none")
-			cfg.Addresses.Swarm = []string{fmt.Sprintf("/ip4/127.0.0.1/tcp/%d", newRandPort())}
+			cfg.Addresses.Swarm = []string{fmt.Sprintf("/ip4/127.0.0.1/tcp/%d", NewRandPort())}
 		})
 
 	})
```

### test/cli/transports_test.go
```diff
@@ -1,6 +1,7 @@
 package cli
 
 import (
+	"fmt"
 	"os"
 	"path/filepath"
 	"testing"
@@ -124,4 +125,26 @@ func TestTransports(t *testing.T) {
 		runTests(nodes)
 	})
 
+	t.Run("QUIC connects with non-dialable transports", func(t *testing.T) {
+		// This test targets specific Kubo internals which may change later. This checks
+		// if we can announce an address we do not listen on, and then are able to connect
+		// via a different address that is available.
+		t.Parallel()
+		nodes := harness.NewT(t).NewNodes(5).Init()
+		nodes.ForEachPar(func(n *harness.Node) {
+			n.UpdateConfig(func(cfg *config.Config) {
+				// We need a specific port to announce so we first generate a random port.
+				// We can't use 0 here to automatically assign an available port because
+				// that would only work with Swarm, but not for the announcing.
+				port := harness.NewRandPort()
+				quicAddr := fmt.Sprintf("/ip4/127.0.0.1/udp/%d/quic-v1", port)
+				cfg.Addresses.Swarm = []string{quicAddr}
+				cfg.Addresses.Announce = []string{quicAddr, quicAddr + "/webtransport"}
+			})
+		})
+		disableRouting(nodes)
+		nodes.StartDaemons().Connect()
+		runTests(nodes)
+	})
+
 }
```
