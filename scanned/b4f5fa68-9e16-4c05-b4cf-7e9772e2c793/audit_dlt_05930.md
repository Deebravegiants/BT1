# [?] core/bootstrap: fix panic without backup bootstrap peer functions (#10029)

## Summary
Severity: Unknown
Chain: IPFS
Component: ipfs/kubo
Published: 2023-09-21
Source: https://github.com/ipfs/kubo/commit/c46cbecb832b9a25f74a275b946b3a0ff3aefaba
Type: security-commit

## Details
core/bootstrap: fix panic without backup bootstrap peer functions (#10029)

Fix panic when backup bootstrap peer load and save funcs are nil

A panic occurs when the first bootstrap round runs is these functions are not assigned in the configuration:
- `LoadBackupBootstrapPeers`
- `SaveBackupBootstrapPeers`

This fix assumes that it is acceptable for these functions to be nil, as it may be desirable to disable the backup peer load and save functionality.

## Patch
### core/bootstrap/bootstrap.go
```diff
@@ -59,8 +59,8 @@ type BootstrapConfig struct {
 	// as backup bootstrap peers.
 	MaxBackupBootstrapSize int
 
-	SaveBackupBootstrapPeers func(context.Context, []peer.AddrInfo)
-	LoadBackupBootstrapPeers func(context.Context) []peer.AddrInfo
+	saveBackupBootstrapPeers func(context.Context, []peer.AddrInfo)
+	loadBackupBootstrapPeers func(context.Context) []peer.AddrInfo
 }
 
 // DefaultBootstrapConfig specifies default sane parameters for bootstrapping.
@@ -72,14 +72,41 @@ var DefaultBootstrapConfig = BootstrapConfig{
 	MaxBackupBootstrapSize:  20,
 }
 
-func BootstrapConfigWithPeers(pis []peer.AddrInfo) BootstrapConfig {
+// BootstrapConfigWithPeers creates a default BootstrapConfig configured with
+// the specified peers, and optional functions to load and save backup peers.
+func BootstrapConfigWithPeers(pis []peer.AddrInfo, options ...func(*BootstrapConfig)) BootstrapConfig {
 	cfg := DefaultBootstrapConfig
 	cfg.BootstrapPeers = func() []peer.AddrInfo {
 		return pis
 	}
+	for _, opt := range options {
+		opt(&cfg)
+	}
 	return cfg
 }
 
+// WithBackupPeers configures functions to load and save backup bootstrap peers.
+func WithBackupPeers(load func(context.Context) []peer.AddrInfo, save func(context.Context, []peer.AddrInfo)) func(*BootstrapConfig) {
+	if save == nil && load != nil || save != nil && load == nil {
+		panic("both load and save backup bootstrap peers functions must be defined")
+	}
+	return func(cfg *BootstrapConfig) {
+		cfg.loadBackupBootstrapPeers = load
+		cfg.saveBackupBootstrapPeers = save
+	}
+}
+
+// BackupPeers returns the load and save backup peers functions.
+func (cfg *BootstrapConfig) BackupPeers() (func(context.Context) []peer.AddrInfo, func(context.Context, []peer.AddrInfo)) {
+	return cfg.loadBackupBootstrapPeers, cfg.saveBackupBootstrapPeers
+}
+
+// SetBackupPeers sets the load and save backup peers functions.
+func (cfg *BootstrapConfig) SetBackupPeers(load func(context.Context) []peer.AddrInfo, save func(context.Context, []peer.AddrInfo)) {
+	opt := WithBackupPeers(load, save)
+	opt(cfg)
+}
+
 // Bootstrap kicks off IpfsNode bootstrapping. This function will periodically
 // check the number of open connections and -- if there are too few -- initiate
 // connections to well-known bootstrap peers. It also kicks off subsystem
@@ -124,7 +151,11 @@ func Bootstrap(id peer.ID, host host.Host, rt routing.Routing, cfg BootstrapConf
 	doneWithRound <- struct{}{}
 	close(doneWithRound) // it no longer blocks periodic
 
-	startSavePeersAsTemporaryBootstrapProc(cfg, host, proc)
+	// If loadBackupBootstrapPeers is not nil then saveBackupBootstrapPeers
+	// must also not be nil.
+	if cfg.loadBackupBootstrapPeers != nil {
+		startSavePeersAsTemporaryBootstrapProc(cfg, host, proc)
+	}
 
 	return proc, nil
 }
@@ -185,7 +216,7 @@ func saveConnectedPeersAsTemporaryBootstrap(ctx context.Context, host host.Host,
 
 	// If we didn't reach the target number use previously stored connected peers.
 	if len(backupPeers) < cfg.MaxBackupBootstrapSize {
-		oldSavedPeers := cfg.LoadBackupBootstrapPeers(ctx)
+		oldSavedPeers := cfg.loadBackupBootstrapPeers(ctx)
 		log.Debugf("missing %d peers to reach backup bootstrap target of %d, trying from previous list of %d saved peers",
 			cfg.MaxBackupBootstrapSize-len(backupPeers), cfg.MaxBackupBootstrapSize, len(oldSavedPeers))
 
@@ -209,7 +240,7 @@ func saveConnectedPeersAsTemporaryBootstrap(ctx context.Context, host host.Host,
 		}
 	}
 
-	cfg.SaveBackupBootstrapPeers(ctx, backupPeers)
+	cfg.saveBackupBootstrapPeers(ctx, backupPeers)
 	log.Debugf("saved %d peers (of %d target) as bootstrap backup in the config", len(backupPeers), cfg.MaxBackupBootstrapSize)
 	return nil
 }
@@ -241,9 +272,14 @@ func bootstrapRound(ctx context.Context, host host.Host, cfg BootstrapConfig) er
 		}
 	}
 
+	if cfg.loadBackupBootstrapPeers == nil {
+		log.Debugf("not enough bootstrap peers to fill the remaining target of %d connections", numToDial)
+		return ErrNotEnoughBootstrapPeers
+	}
+
 	log.Debugf("not enough bootstrap peers to fill the remaining target of %d connections, trying backup list", numToDial)
 
-	tempBootstrapPeers := cfg.LoadBackupBootstrapPeers(ctx)
+	tempBootstrapPeers := cfg.loadBackupBootstrapPeers(ctx)
 	if len(tempBootstrapPeers) > 0 {
 		numToDial -= int(peersConnect(ctx, host, tempBootstrapPeers, numToDial, false))
 		if numToDial <= 0 {
```

### core/bootstrap/bootstrap_test.go
```diff
@@ -1,8 +1,14 @@
 package bootstrap
 
 import (
+	"context"
+	"crypto/rand"
+	"reflect"
 	"testing"
+	"time"
 
+	"github.com/libp2p/go-libp2p"
+	"github.com/libp2p/go-libp2p/core/crypto"
 	"github.com/libp2p/go-libp2p/core/peer"
 	"github.com/libp2p/go-libp2p/core/test"
 )
@@ -23,3 +29,111 @@ func TestRandomizeAddressList(t *testing.T) {
 		t.Fail()
 	}
 }
+
+func TestLoadAndSaveOptions(t *testing.T) {
+	loadFunc := func(_ context.Context) []peer.AddrInfo { return nil }
+	saveFunc := func(_ context.Context, _ []peer.AddrInfo) {}
+
+	bootCfg := BootstrapConfigWithPeers(nil, WithBackupPeers(loadFunc, saveFunc))
+	load, save := bootCfg.BackupPeers()
+	if load == nil {
+		t.Fatal("load function not assigned")
+	}
+	if reflect.ValueOf(load).Pointer() != reflect.ValueOf(loadFunc).Pointer() {
+		t.Fatal("load not assigned correct function")
+	}
+	if save == nil {
+		t.Fatal("save function not assigned")
+	}
+	if reflect.ValueOf(save).Pointer() != reflect.ValueOf(saveFunc).Pointer() {
+		t.Fatal("save not assigned correct function")
+	}
+
+	assertPanics(t, "with only load func", func() {
+		BootstrapConfigWithPeers(nil, WithBackupPeers(loadFunc, nil))
+	})
+
+	assertPanics(t, "with only save func", func() {
+		BootstrapConfigWithPeers(nil, WithBackupPeers(nil, saveFunc))
+	})
+
+	bootCfg = BootstrapConfigWithPeers(nil, WithBackupPeers(nil, nil))
+	load, save = bootCfg.BackupPeers()
+	if load != nil || save != nil {
+		t.Fatal("load and save functions should both be nil")
+	}
+}
+
+func TestSetBackupPeers(t *testing.T) {
+	loadFunc := func(_ context.Context) []peer.AddrInfo { return nil }
+	saveFunc := func(_ context.Context, _ []peer.AddrInfo) {}
+
+	bootCfg := DefaultBootstrapConfig
+	bootCfg.SetBackupPeers(loadFunc, saveFunc)
+	load, save := bootCfg.BackupPeers()
+	if load == nil {
+		t.Fatal("load function not assigned")
+	}
+	if reflect.ValueOf(load).Pointer() != reflect.ValueOf(loadFunc).Pointer() {
+		t.Fatal("load not assigned correct function")
+	}
+	if save == nil {
+		t.Fatal("save function not assigned")
+	}
+	if reflect.ValueOf(save).Pointer() != reflect.ValueOf(saveFunc).Pointer() {
+		t.Fatal("save not assigned correct function")
+	}
+
+	assertPanics(t, "with only load func", func() {
+		bootCfg.SetBackupPeers(loadFunc, nil)
+	})
+
+	assertPanics(t, "with only save func", func() {
+		bootCfg.SetBackupPeers(nil, saveFunc)
+	})
+
+	bootCfg.SetBackupPeers(nil, nil)
+	load, save = bootCfg.BackupPeers()
+	if load != nil || save != nil {
+		t.Fatal("load and save functions should both be nil")
+	}
+}
+
+func TestNoTempPeersLoadAndSave(t *testing.T) {
+	period := 500 * time.Millisecond
+	bootCfg := BootstrapConfigWithPeers(nil)
+	bootCfg.MinPeerThreshold = 2
+	bootCfg.Period = period
+
+	priv, pub, err := crypto.GenerateEd25519Key(rand.Reader)
+	if err != nil {
+		t.Fatal(err)
+	}
+	peerID, err := peer.IDFromPublicKey(pub)
+	if err != nil {
+		t.Fatal(err)
+	}
+	p2pHost, err := libp2p.New(libp2p.Identity(priv))
+	if err != nil {
+		t.Fatal(err)
+	}
+
+	bootstrapper, err := Bootstrap(peerID, p2pHost, nil, bootCfg)
+	if err != nil {
+		t.Fatal(err)
+	}
+
+	time.Sleep(4 * period)
+	bootstrapper.Close()
+
+}
+
+func assertPanics(t *testing.T, name string, f func()) {
+	defer func() {
+		if r := recover(); r == nil {
+			t.Errorf("%s: did not panic as expected", name)
+		}
+	}()
+
+	f()
+}
```

### core/core.go
```diff
@@ -168,24 +168,23 @@ func (n *IpfsNode) Bootstrap(cfg bootstrap.BootstrapConfig) error {
 			return ps
 		}
 	}
-	if cfg.SaveBackupBootstrapPeers == nil {
-		cfg.SaveBackupBootstrapPeers = func(ctx context.Context, peerList []peer.AddrInfo) {
+	if load, _ := cfg.BackupPeers(); load == nil {
+		save := func(ctx context.Context, peerList []peer.AddrInfo) {
 			err := n.saveTempBootstrapPeers(ctx, peerList)
 			if err != nil {
 				log.Warnf("saveTempBootstrapPeers failed: %s", err)
 				return
 			}
 		}
-	}
-	if cfg.LoadBackupBootstrapPeers == nil {
-		cfg.LoadBackupBootstrapPeers = func(ctx context.Context) []peer.AddrInfo {
+		load = func(ctx context.Context) []peer.AddrInfo {
 			peerList, err := n.loadTempBootstrapPeers(ctx)
 			if err != nil {
 				log.Warnf("loadTempBootstrapPeers failed: %s", err)
 				return nil
 			}
 			return peerList
 		}
+		cfg.SetBackupPeers(load, save)
 	}
 
 	repoConf, err := n.Repo.Config()
```
