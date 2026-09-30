# [?] fix: mocha sync, os race condition, add retries to TestRun (#7388)

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-app
Published: 2026-06-11
Source: https://github.com/celestiaorg/celestia-app/commit/72b4a2c9ef6cb6e33f286683f4e795fc17168838
Type: security-commit

## Details
fix: mocha sync, os race condition, add retries to TestRun (#7388)

<!--
Please read and fill out this form before submitting your PR.

Please make sure you have reviewed our contributors guide before
submitting your
first PR.
-->

## Overview

This PR attempts to fix a few race test failures.

- a lot of peers were stale, dynamically fetch during test
- use t.Setenv instead of os.SetEnv (os.Clearenv effects other tests)
- add retries on cmtApp construction to check for duplicate port binding

<!-- 
Please provide an explanation of the PR, including the appropriate
context,
background, goal, and rationale. If there is an issue with this
information,
please provide a tl;dr and link the issue. 
-->

## Patch
### test/cmd/txsim/cli_test.go
```diff
@@ -2,7 +2,6 @@ package main
 
 import (
 	"context"
-	"os"
 	"testing"
 	"time"
 
@@ -45,10 +44,9 @@ func TestTxsimCommandEnvVar(t *testing.T) {
 	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
 	defer cancel()
 
-	os.Setenv(TxsimMnemonic, testfactory.TestAccMnemo)
-	os.Setenv(TxsimGRPC, grpcAddr)
-	os.Setenv(TxsimSeed, "1234")
-	defer os.Clearenv()
+	t.Setenv(TxsimMnemonic, testfactory.TestAccMnemo)
+	t.Setenv(TxsimGRPC, grpcAddr)
+	t.Setenv(TxsimSeed, "1234")
 	cmd.SetArgs([]string{
 		"--blob", "5",
 	})
@@ -59,7 +57,7 @@ func TestTxsimCommandEnvVar(t *testing.T) {
 func TestTxsimDefaultKeypath(t *testing.T) {
 	_, _, grpcAddr := setup(t)
 	cdc := encoding.MakeConfig(app.ModuleEncodingRegisters...).Codec
-	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
+	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
 	defer cancel()
 
 	kr, err := keyring.New(app.Name, keyring.BackendTest, app.NodeHome, nil, cdc)
```

### test/docker-e2e/e2e_sync_to_tip_test.go
```diff
@@ -57,12 +57,16 @@ func (s *CelestiaTestSuite) TestSyncToTipMocha() {
 	dockerCfg, err := networks.NewConfig(mochaConfig, s.client, s.network)
 	s.Require().NoError(err, "failed to create mocha config")
 
+	// fetch live peers from RPC /net_info endpoints so we don't rely on a
+	// hardcoded list that goes stale over time.
+	peers := networks.FetchPeers(t, mochaConfig.RPCs, 10)
+
 	startArgs := []string{"--force-no-bbr"}
 	if mochaConfig.Seeds != "" {
 		startArgs = append(startArgs, fmt.Sprintf("--p2p.seeds=%s", mochaConfig.Seeds))
 	}
-	if mochaConfig.Peers != "" {
-		startArgs = append(startArgs, fmt.Sprintf("--p2p.persistent_peers=%s", mochaConfig.Peers))
+	if peers != "" {
+		startArgs = append(startArgs, fmt.Sprintf("--p2p.persistent_peers=%s", peers))
 	}
 
 	builder := networks.NewChainBuilder(s.T(), mochaConfig, dockerCfg)
```

### test/docker-e2e/networks/config.go
```diff
@@ -11,9 +11,8 @@ type Config struct {
 	Name    string
 	ChainID string
 	RPCs    []string
-	GRPCs   []string
-	Seeds   string
-	Peers   string
+	GRPCs []string
+	Seeds string
 }
 
 // NewMochaConfig returns a Config for the mocha testnet
@@ -30,8 +29,10 @@ func NewMochaConfig() *Config {
 			"https://rpc-mocha.pops.one:443",
 			"https://full.consensus.mocha-4.celestia-mocha.com:443",
 		},
-		Seeds:   "b402fe40f3474e9e208840702e1b7aa37f2edc4b@celestia-testnet-seed.itrocket.net:14656,ee9f90974f85c59d3861fc7f7edb10894f6ac3c8@seed-mocha.pops.one:26656",
-		Peers:   "daf2cecee2bd7f1b3bf94839f993f807c6b15fbf@celestia-testnet-peer.itrocket.net:11656,96b2761729cea90ee7c61206433fc0ba40c245bf@57.128.141.126:11656,f4f75a55bfc5f302ef34435ef096a4551ecb6804@152.53.33.96:12056,31bb1c9c1be7743d1115a8270bd1c83d01a9120a@148.72.141.31:26676,3e30bcfc55e7d351f18144aab4b0973e9e9bf987@65.108.226.183:11656,7a0d5818c0e5b0d4fbd86a9921f413f5e4e4ac1e@65.109.83.40:28656,43e9da043318a4ea0141259c17fcb06ecff816af@164.132.247.253:43656,5a7566aa030f7e5e7114dc9764f944b2b1324bcd@65.109.23.114:11656,c17c0cbf05e98656fee5f60fad469fc528f6d6de@65.109.25.113:11656,fb5e0b9efacc11916c58bbcd3606cbaa7d43c99f@65.108.234.84:28656,45504fb31eb97ea8778c920701fc8076e568a9cd@188.214.133.100:26656,edafdf47c443344fb940a32ab9d2067c482e59df@84.32.71.47:26656,ae7d00d6d70d9b9118c31ac0913e0808f2613a75@177.54.156.69:26656,7c841f59c35d70d9f1472d7d2a76a11eefb7f51f@136.243.69.100:43656",
+		// seeds provide dynamic peer discovery — the node contacts a seed,
+		// gets a fresh list of currently-alive peers, and connects. This is
+		// more resilient than hardcoded persistent peers which go stale.
+		Seeds: "b402fe40f3474e9e208840702e1b7aa37f2edc4b@celestia-testnet-seed.itrocket.net:14656,ee9f90974f85c59d3861fc7f7edb10894f6ac3c8@seed-mocha.pops.one:26656",
 	}
 }
 
```

### test/docker-e2e/networks/config_test.go
```diff
@@ -7,40 +7,19 @@ import (
 
 func TestMochaConfigUpdate(t *testing.T) {
 	config := NewMochaConfig()
-	
-	// Verify seeds configuration
+
 	if !strings.Contains(config.Seeds, "14656") {
 		t.Errorf("Expected seeds to use port 14656, got: %s", config.Seeds)
 	}
-	
+
 	if !strings.HasPrefix(config.Seeds, "b402fe40") {
 		t.Errorf("Expected seeds to start with b402fe40, got: %s", config.Seeds)
 	}
-	
-	// Verify peers configuration
-	if config.Peers == "" {
-		t.Error("Expected peers to be configured, got empty string")
-	}
-	
-	peerList := strings.Split(config.Peers, ",")
-	if len(peerList) != 14 {
-		t.Errorf("Expected 14 peers, got %d", len(peerList))
-	}
-	
-	// Verify at least one known peer
-	hasItrocketPeer := false
-	for _, peer := range peerList {
-		if strings.Contains(peer, "celestia-testnet-peer.itrocket.net:11656") {
-			hasItrocketPeer = true
-			break
-		}
-	}
-	
-	if !hasItrocketPeer {
-		t.Error("Expected to find itrocket peer in peer list")
+
+	seedList := strings.Split(config.Seeds, ",")
+	if len(seedList) < 2 {
+		t.Errorf("Expected at least 2 seeds, got %d", len(seedList))
 	}
-	
-	t.Logf("Mocha config updated successfully with %d peers and correct seeds", len(peerList))
 }
 
 // TestMochaConfigRPCsAreDistinct verifies that the mocha RPC list contains at
```

### test/docker-e2e/networks/networks.go
```diff
@@ -1,10 +1,14 @@
 package networks
 
 import (
+	"context"
 	"fmt"
 	"io"
+	"net"
 	"net/http"
+	"strings"
 	"testing"
+	"time"
 
 	tastoratypes "github.com/celestiaorg/tastora/framework/types"
 
@@ -58,6 +62,64 @@ func NewClient(rpc string) (*rpchttp.HTTP, error) {
 	return rpchttp.New(rpc, "/websocket")
 }
 
+// FetchPeers queries /net_info on each RPC endpoint and returns a
+// deduplicated, comma-separated list of peers suitable for
+// --p2p.persistent_peers. It tries every RPC in the config and merges results
+// so that transient failures on a single provider don't leave us with zero
+// peers. maxPeers caps the returned list to avoid bloating the arg.
+func FetchPeers(t *testing.T, rpcs []string, maxPeers int) string {
+	t.Helper()
+
+	seen := make(map[string]struct{})
+	var peers []string
+
+	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
+	defer cancel()
+
+	for _, rpc := range rpcs {
+		if len(peers) >= maxPeers {
+			break
+		}
+		client, err := NewClient(rpc)
+		if err != nil {
+			t.Logf("FetchPeers: %s: %v", rpc, err)
+			continue
+		}
+		netInfo, err := client.NetInfo(ctx)
+		if err != nil {
+			t.Logf("FetchPeers: %s: %v", rpc, err)
+			continue
+		}
+		for _, p := range netInfo.Peers {
+			id := string(p.NodeInfo.DefaultNodeID)
+			if id == "" || p.RemoteIP == "" {
+				continue
+			}
+			// skip IPv6 peers — CometBFT's persistent_peers format
+			// doesn't reliably handle IPv6 addresses.
+			if net.ParseIP(p.RemoteIP) != nil && strings.Contains(p.RemoteIP, ":") {
+				continue
+			}
+			if _, ok := seen[id]; ok {
+				continue
+			}
+			seen[id] = struct{}{}
+			// extract port from listen_addr (e.g. "tcp://0.0.0.0:26656")
+			port := "26656"
+			if parts := strings.Split(p.NodeInfo.ListenAddr, ":"); len(parts) > 1 {
+				port = parts[len(parts)-1]
+			}
+			peers = append(peers, fmt.Sprintf("%s@%s:%s", id, p.RemoteIP, port))
+		}
+	}
+
+	if len(peers) > maxPeers {
+		peers = peers[:maxPeers]
+	}
+	t.Logf("FetchPeers: discovered %d peers from %d RPCs", len(peers), len(rpcs))
+	return strings.Join(peers, ",")
+}
+
 // downloadGenesis downloads the genesis file for the given chain ID from the celestia networks repo
 func downloadGenesis(chainID string) ([]byte, error) {
 	url := fmt.Sprintf("https://raw.githubusercontent.com/celestiaorg/networks/master/%s/genesis.json", chainID)
```

### test/util/testnode/network.go
```diff
@@ -33,7 +33,7 @@ func NewNetworkWithRetry(t testing.TB, config *Config, maxRetries int) (cctx Con
 			if cleanup != nil {
 				cleanup()
 			}
-			if isPortBindingError(err) {
+			if IsPortBindingError(err) {
 				t.Logf("port binding error on attempt %d/%d, retrying after %ds: %v", attempt+1, maxRetries, attempt+1, err)
 				time.Sleep(time.Duration(attempt+1) * time.Second)
 				reassignListenPorts(config)
@@ -133,14 +133,13 @@ func reassignListenPorts(config *Config) {
 	config.AppConfig.API.Address = fmt.Sprintf("tcp://127.0.0.1:%d", GetDeterministicPort())
 }
 
-// isPortBindingError checks if an error is related to port binding failures
-func isPortBindingError(err error) bool {
+// IsPortBindingError checks if an error is related to port binding failures.
+func IsPortBindingError(err error) bool {
 	if err == nil {
 		return false
 	}
 	errStr := err.Error()
 	// Check for common port binding error patterns
-	return strings.Contains(errStr, "bind: address already in use") ||
-		strings.Contains(errStr, "address already in use") ||
+	return strings.Contains(errStr, "address already in use") ||
 		strings.Contains(errStr, "failed to listen on")
 }
```

### tools/chainbuilder/integration_test.go
```diff
@@ -54,41 +54,59 @@ func TestRun(t *testing.T) {
 	err = Run(context.Background(), cfg, dir)
 	require.NoError(t, err)
 
-	tmCfg := testnode.DefaultTendermintConfig()
-	tmCfg.SetRoot(cfg.ExistingDir)
-
-	appDB, err := tmdbm.NewDB("application", tmdbm.BackendType(tmCfg.DBBackend), tmCfg.DBDir())
-	require.NoError(t, err)
-	t.Cleanup(func() { _ = appDB.Close() })
-
-	app := app.New(
-		log.NewNopLogger(),
-		appDB,
-		nil,
-		0, // delayed precommit timeout
-		0, // timeout commit
-		util.EmptyAppOptions{},
-		baseapp.SetMinGasPrices(fmt.Sprintf("%f%s", appconsts.DefaultMinGasPrice, appconsts.BondDenom)),
-	)
-
-	nodeKey, err := p2p.LoadNodeKey(tmCfg.NodeKeyFile())
-	require.NoError(t, err)
+	// retry node start with fresh ports on binding errors (TOCTOU in
+	// GetDeterministicPort can cause collisions under -race).
+	const maxRetries = 3
+	var cometNode *node.Node
+	for attempt := range maxRetries {
+		tmCfg := testnode.DefaultTendermintConfig()
+		tmCfg.SetRoot(cfg.ExistingDir)
+
+		appDB, err := tmdbm.NewDB("application", tmdbm.BackendType(tmCfg.DBBackend), tmCfg.DBDir())
+		require.NoError(t, err)
 
-	cmtApp := server.NewCometABCIWrapper(app)
-	cometNode, err := node.NewNode(
-		tmCfg,
-		privval.LoadOrGenFilePV(tmCfg.PrivValidatorKeyFile(), tmCfg.PrivValidatorStateFile()),
-		nodeKey,
-		proxy.NewLocalClientCreator(cmtApp),
-		getGenDocProvider(tmCfg),
-		cmtcfg.DefaultDBProvider,
-		node.DefaultMetricsProvider(tmCfg.Instrumentation),
-		tmlog.NewNopLogger(),
-	)
-	require.NoError(t, err)
+		celestiaApp := app.New(
+			log.NewNopLogger(),
+			appDB,
+			nil,
+			0, // delayed precommit timeout
+			0, // timeout commit
+			util.EmptyAppOptions{},
+			baseapp.SetMinGasPrices(fmt.Sprintf("%f%s", appconsts.DefaultMinGasPrice, appconsts.BondDenom)),
+		)
+
+		nodeKey, err := p2p.LoadNodeKey(tmCfg.NodeKeyFile())
+		require.NoError(t, err)
 
-	require.NoError(t, cometNode.Start())
-	defer func() { _ = cometNode.Stop() }()
+		cmtApp := server.NewCometABCIWrapper(celestiaApp)
+		cometNode, err = node.NewNode(
+			tmCfg,
+			privval.LoadOrGenFilePV(tmCfg.PrivValidatorKeyFile(), tmCfg.PrivValidatorStateFile()),
+			nodeKey,
+			proxy.NewLocalClientCreator(cmtApp),
+			getGenDocProvider(tmCfg),
+			cmtcfg.DefaultDBProvider,
+			node.DefaultMetricsProvider(tmCfg.Instrumentation),
+			tmlog.NewNopLogger(),
+		)
+		if err == nil {
+			err = cometNode.Start()
+		}
+		if err != nil {
+			_ = appDB.Close()
+			if testnode.IsPortBindingError(err) && attempt < maxRetries-1 {
+				t.Logf("port binding error on attempt %d/%d, retrying: %v", attempt+1, maxRetries, err)
+				time.Sleep(time.Duration(attempt+1) * time.Second)
+				continue
+			}
+			require.NoError(t, err)
+		}
+		break
+	}
+	defer func() {
+		_ = cometNode.Stop()
+		cometNode.Wait()
+	}()
 
 	client := local.New(cometNode)
 	status, err := client.Status(context.Background())
@@ -100,8 +118,6 @@ func TestRun(t *testing.T) {
 		require.NoError(t, err)
 		return status.SyncInfo.LatestBlockHeight >= int64(numBlocks*2)
 	}, time.Second*10, time.Millisecond*100)
-	require.NoError(t, cometNode.Stop())
-	cometNode.Wait()
 }
 
 // getGenDocProvider returns a function that loads the genesis document from file.
```
