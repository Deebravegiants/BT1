# [?] BCF-2562: fix nil panic caused by missing configuration (#10296)

## Summary
Severity: Unknown
Chain: Bridge
Component: smartcontractkit/ccip
Published: 2023-08-24
Source: https://github.com/smartcontractkit/ccip/commit/ea436d24be099fa5abb99f6d39f0755669864698
Type: security-commit

## Details
BCF-2562: fix nil panic caused by missing configuration (#10296)

* BCF-2562: fix nil panic caused by missing configuration

* better error messages

* remove debugging code

* make lazy init thread safe and add test

* graphql logging and fix test

## Patch
### core/chains/chain_set.go
```diff
@@ -80,7 +80,7 @@ func (c *chainSet[N, S]) Chain(ctx context.Context, id string) (s S, err error)
 	}
 	ch, ok := c.chains[id]
 	if !ok {
-		err = ErrNotFound
+		err = fmt.Errorf("chain %s: %w", id, ErrNotFound)
 		return
 	}
 	return ch, nil
@@ -94,7 +94,7 @@ func (c *chainSet[N, S]) ChainStatus(ctx context.Context, id string) (cfg types.
 	}
 	l := len(cs)
 	if l == 0 {
-		err = ErrNotFound
+		err = fmt.Errorf("chain %s: %w", id, ErrNotFound)
 		return
 	}
 	if l > 1 {
```

### core/chains/cosmos/config.go
```diff
@@ -115,7 +115,7 @@ func (cs CosmosConfigs) Node(name string) (n db.Node, err error) {
 			}
 		}
 	}
-	err = chains.ErrNotFound
+	err = fmt.Errorf("node %s: %w", name, chains.ErrNotFound)
 	return
 }
 
@@ -131,7 +131,7 @@ func (cs CosmosConfigs) nodes(chainID string) (ns CosmosNodes) {
 func (cs CosmosConfigs) Nodes(chainID string) (ns []db.Node, err error) {
 	nodes := cs.nodes(chainID)
 	if nodes == nil {
-		err = chains.ErrNotFound
+		err = fmt.Errorf("no nodes: chain %s: %w", chainID, chains.ErrNotFound)
 		return
 	}
 	for _, n := range nodes {
@@ -152,7 +152,7 @@ func (cs CosmosConfigs) NodeStatus(name string) (n relaytypes.NodeStatus, err er
 			}
 		}
 	}
-	err = chains.ErrNotFound
+	err = fmt.Errorf("node %s: %w", name, chains.ErrNotFound)
 	return
 }
 
```

### core/chains/evm/chain.go
```diff
@@ -6,6 +6,7 @@ import (
 	"fmt"
 	"math/big"
 	"net/url"
+	"sync"
 	"time"
 
 	"go.uber.org/multierr"
@@ -83,11 +84,14 @@ type LegacyChainContainer interface {
 
 var _ LegacyChainContainer = &LegacyChains{}
 
-func NewLegacyChains(c evmtypes.Configs, m map[string]Chain) *LegacyChains {
+func NewLegacyChains(cfg AppConfig, m map[string]Chain) (*LegacyChains, error) {
+	if cfg == nil {
+		return nil, fmt.Errorf("must provide non-nil app config")
+	}
 	return &LegacyChains{
 		ChainsKV: chains.NewChainsKV[Chain](m),
-		cfgs:     c,
-	}
+		cfgs:     chains.NewConfigs[utils.Big, evmtypes.Node](cfg.EVMConfigs()),
+	}, nil
 }
 
 func (c *LegacyChains) ChainNodeConfigs() evmtypes.Configs {
@@ -161,12 +165,14 @@ type ChainRelayExtenderConfig struct {
 // the factory wants to own the logger and db
 // the factory creates extenders, which need the same and more opts
 type RelayerConfig struct {
-	GeneralConfig AppConfig
+	AppConfig AppConfig
 
-	EventBroadcaster   pg.EventBroadcaster
-	MailMon            *utils.MailboxMonitor
-	GasEstimator       gas.EvmFeeEstimator
-	OperationalConfigs evmtypes.Configs
+	EventBroadcaster pg.EventBroadcaster
+	MailMon          *utils.MailboxMonitor
+	GasEstimator     gas.EvmFeeEstimator
+
+	init               sync.Once
+	operationalConfigs evmtypes.Configs
 
 	// TODO BCF-2513 remove test code from the API
 	// Gen-functions are useful for dependency injection by tests
@@ -178,13 +184,21 @@ type RelayerConfig struct {
 	GenGasEstimator   func(*big.Int) gas.EvmFeeEstimator
 }
 
+func (r *RelayerConfig) EVMConfigs() evmtypes.Configs {
+	if r.operationalConfigs == nil {
+		r.init.Do(func() {
+			r.operationalConfigs = chains.NewConfigs[utils.Big, evmtypes.Node](r.AppConfig.EVMConfigs())
+		})
+	}
+	return r.operationalConfigs
+}
 func NewTOMLChain(ctx context.Context, chain *toml.EVMConfig, opts ChainRelayExtenderConfig) (Chain, error) {
 	chainID := chain.ChainID
 	l := opts.Logger.With("evmChainID", chainID.String())
 	if !chain.IsEnabled() {
 		return nil, errChainDisabled{ChainID: chainID}
 	}
-	cfg := evmconfig.NewTOMLChainScopedConfig(opts.GeneralConfig, chain, l)
+	cfg := evmconfig.NewTOMLChainScopedConfig(opts.AppConfig, chain, l)
 	// note: per-chain validation is not necessary at this point since everything is checked earlier on boot.
 	return newChain(ctx, cfg, chain.Nodes, opts)
 }
@@ -412,10 +426,10 @@ func (opts *ChainRelayExtenderConfig) Check() error {
 	if opts.Logger == nil {
 		return errors.New("logger must be non-nil")
 	}
-	if opts.GeneralConfig == nil {
+	if opts.AppConfig == nil {
 		return errors.New("config must be non-nil")
 	}
 
-	opts.OperationalConfigs = chains.NewConfigs[utils.Big, evmtypes.Node](opts.GeneralConfig.EVMConfigs())
+	opts.operationalConfigs = chains.NewConfigs[utils.Big, evmtypes.Node](opts.AppConfig.EVMConfigs())
 	return nil
 }
```

### core/chains/evm/chain_test.go
```diff
@@ -0,0 +1,54 @@
+package evm_test
+
+import (
+	"math/big"
+	"testing"
+
+	"github.com/stretchr/testify/assert"
+
+	"github.com/smartcontractkit/chainlink/v2/core/chains/evm"
+	"github.com/smartcontractkit/chainlink/v2/core/chains/evm/mocks"
+	configtest "github.com/smartcontractkit/chainlink/v2/core/internal/testutils/configtest/v2"
+	"github.com/smartcontractkit/chainlink/v2/core/services/chainlink"
+	"github.com/smartcontractkit/chainlink/v2/core/utils"
+)
+
+func TestLegacyChains(t *testing.T) {
+	evmCfg := configtest.NewGeneralConfig(t, nil)
+
+	c := mocks.NewChain(t)
+	c.On("ID").Return(big.NewInt(7))
+	m := map[string]evm.Chain{c.ID().String(): c}
+
+	l, err := evm.NewLegacyChains(evmCfg, m)
+	assert.NoError(t, err)
+	assert.NotNil(t, l.ChainNodeConfigs())
+	got, err := l.Get(c.ID().String())
+	assert.NoError(t, err)
+	assert.Equal(t, c, got)
+
+	l, err = evm.NewLegacyChains(nil, m)
+	assert.Error(t, err)
+	assert.Nil(t, l)
+}
+
+func TestRelayConfigInit(t *testing.T) {
+	appCfg := configtest.NewGeneralConfig(t, nil)
+	rCfg := evm.RelayerConfig{
+		AppConfig: appCfg,
+	}
+
+	evmCfg := rCfg.EVMConfigs()
+	assert.NotNil(t, evmCfg)
+
+	// test lazy init is done only once
+	// note this kind of swapping should never happen in prod
+	appCfg2 := configtest.NewGeneralConfig(t, func(c *chainlink.Config, s *chainlink.Secrets) {
+		c.EVM[0].ChainID = utils.NewBig(big.NewInt(27))
+	})
+	rCfg.AppConfig = appCfg2
+
+	newEvmCfg := rCfg.EVMConfigs()
+	assert.NotNil(t, newEvmCfg)
+	assert.Equal(t, evmCfg, newEvmCfg)
+}
```

### core/chains/evm/config/toml/config.go
```diff
@@ -133,7 +133,7 @@ func (cs EVMConfigs) Node(name string) (types.Node, error) {
 			}
 		}
 	}
-	return types.Node{}, chains.ErrNotFound
+	return types.Node{}, fmt.Errorf("node %s: %w", name, chains.ErrNotFound)
 }
 
 func (cs EVMConfigs) NodeStatus(name string) (relaytypes.NodeStatus, error) {
@@ -144,7 +144,7 @@ func (cs EVMConfigs) NodeStatus(name string) (relaytypes.NodeStatus, error) {
 			}
 		}
 	}
-	return relaytypes.NodeStatus{}, chains.ErrNotFound
+	return relaytypes.NodeStatus{}, fmt.Errorf("node %s: %w", name, chains.ErrNotFound)
 }
 
 func legacyNode(n *Node, chainID *utils.Big) (v2 types.Node) {
@@ -190,7 +190,7 @@ func (cs EVMConfigs) Nodes(chainID utils.Big) (ns []types.Node, err error) {
 	id := chainID.String()
 	nodes := cs.nodes(id)
 	if nodes == nil {
-		err = chains.ErrNotFound
+		err = fmt.Errorf("no nodes: chain %s: %w", &chainID, chains.ErrNotFound)
 		return
 	}
 	for _, n := range nodes {
```

### core/chains/evm/log/helpers_test.go
```diff
@@ -121,7 +121,8 @@ func (c broadcasterHelperCfg) newWithEthClient(t *testing.T, ethClient evmclient
 		LogBroadcaster: &log.NullBroadcaster{},
 		MailMon:        mailMon,
 	})
-	legacyChains := evmrelay.NewLegacyChainsFromRelayerExtenders(cc)
+	legacyChains, err := evmrelay.NewLegacyChainsFromRelayerExtenders(cc)
+	require.NoError(t, err)
 	pipelineHelper := cltest.NewJobPipelineV2(t, config.WebServer(), config.JobPipeline(), config.Database(), legacyChains, c.db, kst, nil, nil)
 
 	return &broadcasterHelper{
```

### core/chains/solana/config.go
```diff
@@ -113,7 +113,7 @@ func (cs SolanaConfigs) Node(name string) (soldb.Node, error) {
 			}
 		}
 	}
-	return soldb.Node{}, chains.ErrNotFound
+	return soldb.Node{}, fmt.Errorf("node %s: %w", name, chains.ErrNotFound)
 }
 
 func (cs SolanaConfigs) nodes(chainID string) (ns SolanaNodes) {
@@ -128,7 +128,7 @@ func (cs SolanaConfigs) nodes(chainID string) (ns SolanaNodes) {
 func (cs SolanaConfigs) Nodes(chainID string) (ns []soldb.Node, err error) {
 	nodes := cs.nodes(chainID)
 	if nodes == nil {
-		err = chains.ErrNotFound
+		err = fmt.Errorf("no nodes: chain %s: %w", chainID, chains.ErrNotFound)
 		return
 	}
 	for _, n := range nodes {
@@ -148,7 +148,7 @@ func (cs SolanaConfigs) NodeStatus(name string) (types.NodeStatus, error) {
 			}
 		}
 	}
-	return types.NodeStatus{}, chains.ErrNotFound
+	return types.NodeStatus{}, fmt.Errorf("node %s: %w", name, chains.ErrNotFound)
 }
 
 func (cs SolanaConfigs) NodeStatuses(chainIDs ...string) (ns []types.NodeStatus, err error) {
```

### core/chains/starknet/config.go
```diff
@@ -112,7 +112,7 @@ func (cs StarknetConfigs) Node(name string) (n db.Node, err error) {
 			}
 		}
 	}
-	err = chains.ErrNotFound
+	err = fmt.Errorf("node %s: %w", name, chains.ErrNotFound)
 	return
 }
 
@@ -128,7 +128,7 @@ func (cs StarknetConfigs) nodes(chainID string) (ns StarknetNodes) {
 func (cs StarknetConfigs) Nodes(chainID string) (ns []db.Node, err error) {
 	nodes := cs.nodes(chainID)
 	if nodes == nil {
-		err = chains.ErrNotFound
+		err = fmt.Errorf("no nodes: chain %s: %w", chainID, chains.ErrNotFound)
 		return
 	}
 	for _, n := range nodes {
@@ -148,7 +148,7 @@ func (cs StarknetConfigs) NodeStatus(name string) (n types.NodeStatus, err error
 			}
 		}
 	}
-	err = chains.ErrNotFound
+	err = fmt.Errorf("node %s: %w", name, chains.ErrNotFound)
 	return
 }
 
```

### core/cmd/shell.go
```diff
@@ -156,8 +156,8 @@ func (n ChainlinkAppFactory) NewApplication(ctx context.Context, cfg chainlink.G
 	}
 
 	evmFactoryCfg := chainlink.EVMFactoryConfig{
-		RelayerConfig:  evm.RelayerConfig{GeneralConfig: cfg, EventBroadcaster: eventBroadcaster, MailMon: mailMon},
 		CSAETHKeystore: keyStore,
+		RelayerConfig:  evm.RelayerConfig{AppConfig: cfg, EventBroadcaster: eventBroadcaster, MailMon: mailMon},
 	}
 	// evm always enabled for backward compatibility
 	// TODO BCF-2510 this needs to change in order to clear the path for EVM extraction
```

### core/cmd/shell_local_test.go
```diff
@@ -43,7 +43,7 @@ func genTestEVMRelayers(t *testing.T, opts evm.ChainRelayExtenderConfig, ks evmr
 	f := chainlink.RelayerFactory{
 		Logger:       opts.Logger,
 		DB:           opts.DB,
-		QConfig:      opts.GeneralConfig.Database(),
+		QConfig:      opts.AppConfig.Database(),
 		LoopRegistry: plugins.NewLoopRegistry(opts.Logger),
 	}
 
@@ -90,7 +90,7 @@ func TestShell_RunNodeWithPasswords(t *testing.T) {
 				DB:       db,
 				KeyStore: keyStore.Eth(),
 				RelayerConfig: evm.RelayerConfig{
-					GeneralConfig:    cfg,
+					AppConfig:        cfg,
 					EventBroadcaster: pg.NewNullEventBroadcaster(),
 					MailMon:          &utils.MailboxMonitor{},
 				},
@@ -197,7 +197,7 @@ func TestShell_RunNodeWithAPICredentialsFile(t *testing.T) {
 				DB:       db,
 				KeyStore: keyStore.Eth(),
 				RelayerConfig: evm.RelayerConfig{
-					GeneralConfig:    cfg,
+					AppConfig:        cfg,
 					EventBroadcaster: pg.NewNullEventBroadcaster(),
 
 					MailMon: &utils.MailboxMonitor{},
```

### core/internal/cltest/cltest.go
```diff
@@ -398,7 +398,7 @@ func NewApplicationWithConfig(t testing.TB, cfg chainlink.GeneralConfig, flagsAn
 	chainId := ethClient.ConfiguredChainID()
 	evmOpts := chainlink.EVMFactoryConfig{
 		RelayerConfig: evm.RelayerConfig{
-			GeneralConfig:    cfg,
+			AppConfig:        cfg,
 			EventBroadcaster: eventBroadcaster,
 			MailMon:          mailMon,
 			GenEthClient: func(_ *big.Int) evmclient.Client {
```

### core/internal/cltest/job_factories.go
```diff
@@ -6,6 +6,7 @@ import (
 
 	"github.com/google/uuid"
 	"github.com/smartcontractkit/sqlx"
+	"github.com/stretchr/testify/assert"
 	"github.com/stretchr/testify/require"
 
 	"github.com/smartcontractkit/chainlink/v2/core/bridges"
@@ -65,7 +66,9 @@ func getORMs(t *testing.T, db *sqlx.DB) (jobORM job.ORM, pipelineORM pipeline.OR
 	pipelineORM = pipeline.NewORM(db, lggr, config.Database(), config.JobPipeline().MaxSuccessfulRuns())
 	bridgeORM := bridges.NewORM(db, lggr, config.Database())
 	cc := evmtest.NewChainRelayExtenders(t, evmtest.TestChainOpts{DB: db, GeneralConfig: config, KeyStore: keyStore.Eth()})
-	jobORM = job.NewORM(db, evmrelay.NewLegacyChainsFromRelayerExtenders(cc), pipelineORM, bridgeORM, keyStore, lggr, config.Database())
+	legacyChains, err := evmrelay.NewLegacyChainsFromRelayerExtenders(cc)
+	assert.NoError(t, err)
+	jobORM = job.NewORM(db, legacyChains, pipelineORM, bridgeORM, keyStore, lggr, config.Database())
 	t.Cleanup(func() { jobORM.Close() })
 	return
 }
```
