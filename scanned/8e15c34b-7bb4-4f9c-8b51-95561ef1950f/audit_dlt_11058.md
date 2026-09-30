# [?] fix: Fix blob fee overflow on rollup-relayer and gas-oracle (#1772)

## Summary
Severity: Unknown
Chain: Scroll
Component: scroll-tech/scroll
Published: 2025-11-28
Source: https://github.com/scroll-tech/scroll/commit/752e4e1117d7040dd290632846f789b42afac9f2
Type: security-commit

## Details
fix: Fix blob fee overflow on rollup-relayer and gas-oracle (#1772)

## Patch
### common/testcontainers/docker-compose.yml
```diff
@@ -34,7 +34,7 @@ services:
 
   # Sets up the genesis configuration for the go-ethereum client from a JSON file.
   geth-genesis:
-    image: "ethereum/client-go:v1.13.14"
+    image: "ethereum/client-go:v1.14.0"
     command: --datadir=/data/execution init /data/execution/genesis.json
     volumes:
       - data:/data
@@ -80,7 +80,7 @@ services:
   # Runs the go-ethereum execution client with the specified, unlocked account and necessary
   # APIs to allow for proof-of-stake consensus via Prysm.
   geth:
-    image: "ethereum/client-go:v1.13.14"
+    image: "ethereum/client-go:v1.14.0"
     command:
       - --http
       - --http.api=eth,net,web3
```

### common/testcontainers/docker/l1geth/Dockerfile
```diff
@@ -1,4 +1,4 @@
-FROM ethereum/client-go:v1.13.14
+FROM ethereum/client-go:v1.14.0
 
 COPY password /l1geth/
 COPY genesis.json /l1geth/
```

### common/testcontainers/testcontainers.go
```diff
@@ -167,13 +167,13 @@ func (t *TestcontainerApps) GetPoSL1EndPoint() (string, error) {
 	return contrainer.PortEndpoint(context.Background(), "8545/tcp", "http")
 }
 
-// GetPoSL1Client returns a ethclient by dialing running PoS L1 client
-func (t *TestcontainerApps) GetPoSL1Client() (*ethclient.Client, error) {
+// GetPoSL1Client returns a raw rpc client by dialing the L1 node
+func (t *TestcontainerApps) GetPoSL1Client() (*rpc.Client, error) {
 	endpoint, err := t.GetPoSL1EndPoint()
 	if err != nil {
 		return nil, err
 	}
-	return ethclient.Dial(endpoint)
+	return rpc.Dial(endpoint)
 }
 
 // GetDBEndPoint returns the endpoint of the running postgres container
@@ -221,7 +221,6 @@ func (t *TestcontainerApps) GetGormDBClient() (*gorm.DB, error) {
 
 // GetL2GethClient returns a ethclient by dialing running L2Geth
 func (t *TestcontainerApps) GetL2GethClient() (*ethclient.Client, error) {
-
 	rpcCli, err := t.GetL2Client()
 	if err != nil {
 		return nil, err
```

### common/testcontainers/testcontainers_test.go
```diff
@@ -3,7 +3,6 @@ package testcontainers
 import (
 	"testing"
 
-	"github.com/scroll-tech/go-ethereum/ethclient"
 	"github.com/stretchr/testify/assert"
 	"gorm.io/gorm"
 )
@@ -14,7 +13,6 @@ func TestNewTestcontainerApps(t *testing.T) {
 		err          error
 		endpoint     string
 		gormDBclient *gorm.DB
-		ethclient    *ethclient.Client
 	)
 
 	testApps := NewTestcontainerApps()
@@ -32,17 +30,17 @@ func TestNewTestcontainerApps(t *testing.T) {
 	endpoint, err = testApps.GetL2GethEndPoint()
 	assert.NoError(t, err)
 	assert.NotEmpty(t, endpoint)
-	ethclient, err = testApps.GetL2GethClient()
+	l2RawClient, err := testApps.GetL2Client()
 	assert.NoError(t, err)
-	assert.NotNil(t, ethclient)
+	assert.NotNil(t, l2RawClient)
 
 	assert.NoError(t, testApps.StartPoSL1Container())
 	endpoint, err = testApps.GetPoSL1EndPoint()
 	assert.NoError(t, err)
 	assert.NotEmpty(t, endpoint)
-	ethclient, err = testApps.GetPoSL1Client()
+	l1RawClient, err := testApps.GetPoSL1Client()
 	assert.NoError(t, err)
-	assert.NotNil(t, ethclient)
+	assert.NotNil(t, l1RawClient)
 
 	assert.NoError(t, testApps.StartWeb3SignerContainer(1))
 	endpoint, err = testApps.GetWeb3SignerEndpoint()
```

### common/version/version.go
```diff
@@ -5,7 +5,7 @@ import (
 	"runtime/debug"
 )
 
-var tag = "v4.7.5"
+var tag = "v4.7.6"
 
 var commit = func() string {
 	if info, ok := debug.ReadBuildInfo(); ok {
```

### rollup/cmd/gas_oracle/app/app.go
```diff
@@ -66,17 +66,26 @@ func action(ctx *cli.Context) error {
 	registry := prometheus.DefaultRegisterer
 	observability.Server(ctx, db)
 
-	l1client, err := ethclient.Dial(cfg.L1Config.Endpoint)
+	// Init L1 connection
+	l1RpcClient, err := rpc.Dial(cfg.L1Config.Endpoint)
 	if err != nil {
-		log.Crit("failed to connect l1 geth", "config file", cfgFile, "error", err)
+		log.Crit("failed to dial raw RPC client to L1 endpoint", "endpoint", cfg.L1Config.Endpoint, "error", err)
 	}
+	l1client := ethclient.NewClient(l1RpcClient)
 
-	l1watcher := watcher.NewL1WatcherClient(ctx.Context, l1client, cfg.L1Config.StartHeight, db, registry)
+	// sanity check config
+	if cfg.L1Config.RelayerConfig.GasOracleConfig.L1BaseFeeLimit == 0 || cfg.L1Config.RelayerConfig.GasOracleConfig.L1BlobBaseFeeLimit == 0 {
+		log.Crit("gas-oracle `l1_base_fee_limit` and `l1_blob_base_fee_limit` configs must be set")
+	}
+
+	// Init watcher and relayer
+	l1watcher := watcher.NewL1WatcherClient(ctx.Context, l1RpcClient, cfg.L1Config.StartHeight, db, registry)
 
 	l1relayer, err := relayer.NewLayer1Relayer(ctx.Context, db, cfg.L1Config.RelayerConfig, relayer.ServiceTypeL1GasOracle, registry)
 	if err != nil {
 		log.Crit("failed to create new l1 relayer", "config file", cfgFile, "error", err)
 	}
+
 	// Start l1 watcher process
 	go utils.LoopWithContext(subCtx, 10*time.Second, func(ctx context.Context) {
 		// Fetch the latest block number to decrease the delay when fetching gas prices
```

### rollup/conf/config.json
```diff
@@ -21,7 +21,9 @@
         "check_committed_batches_window_minutes": 5,
         "l1_base_fee_default": 15000000000,
         "l1_blob_base_fee_default": 1,
-        "l1_blob_base_fee_threshold": 0
+        "l1_blob_base_fee_threshold": 0,
+        "l1_base_fee_limit": 20000000000,
+        "l1_blob_base_fee_limit": 20000000000
       },
       "gas_oracle_sender_signer_config": {
         "signer_type": "PrivateKey",
```

### rollup/go.mod
```diff
@@ -51,7 +51,7 @@ require (
 	github.com/cpuguy83/go-md2man/v2 v2.0.3 // indirect
 	github.com/crate-crypto/go-eth-kzg v1.4.0 // indirect
 	github.com/davecgh/go-spew v1.1.2-0.20180830191138-d8f796af33cc // indirect
-	github.com/deckarep/golang-set v0.0.0-20180603214616-504e848d77ea // indirect
+	github.com/deckarep/golang-set v1.8.0 // indirect
 	github.com/edsrzf/mmap-go v1.0.0 // indirect
 	github.com/ethereum/c-kzg-4844/v2 v2.1.5 // indirect
 	github.com/fjl/memsize v0.0.2 // indirect
```

### rollup/go.sum
```diff
@@ -88,8 +88,8 @@ github.com/davecgh/go-spew v1.1.0/go.mod h1:J7Y8YcW2NihsgmVo/mv3lAwl/skON4iLHjSs
 github.com/davecgh/go-spew v1.1.1/go.mod h1:J7Y8YcW2NihsgmVo/mv3lAwl/skON4iLHjSsI+c5H38=
 github.com/davecgh/go-spew v1.1.2-0.20180830191138-d8f796af33cc h1:U9qPSI2PIWSS1VwoXQT9A3Wy9MM3WgvqSxFWenqJduM=
 github.com/davecgh/go-spew v1.1.2-0.20180830191138-d8f796af33cc/go.mod h1:J7Y8YcW2NihsgmVo/mv3lAwl/skON4iLHjSsI+c5H38=
-github.com/deckarep/golang-set v0.0.0-20180603214616-504e848d77ea h1:j4317fAZh7X6GqbFowYdYdI0L9bwxL07jyPZIdepyZ0=
-github.com/deckarep/golang-set v0.0.0-20180603214616-504e848d77ea/go.mod h1:93vsz/8Wt4joVM7c2AVqh+YRMiUSc14yDtF28KmMOgQ=
+github.com/deckarep/golang-set v1.8.0 h1:sk9/l/KqpunDwP7pSjUg0keiOOLEnOBHzykLrsPppp4=
+github.com/deckarep/golang-set v1.8.0/go.mod h1:5nI87KwE7wgsBU1F4GKAw2Qod7p5kyS383rP6+o6qqo=
 github.com/dgryski/go-sip13 v0.0.0-20181026042036-e10d5fee7954/go.mod h1:vAd38F8PWV+bWy6jNmig1y/TA+kYO4g3RSRF0IAv0no=
 github.com/edsrzf/mmap-go v1.0.0 h1:CEBF7HpRnUCSJgGUb5h1Gm7e3VkmVDrR8lvWVLtrOFw=
 github.com/edsrzf/mmap-go v1.0.0/go.mod h1:YO35OhQPt3KJa3ryjFM5Bs14WD66h8eGKpfaBNrHW5M=
```

### rollup/internal/config/relayer.go
```diff
@@ -109,6 +109,10 @@ type GasOracleConfig struct {
 	L1BaseFeeDefault                   uint64 `json:"l1_base_fee_default"`
 	L1BlobBaseFeeDefault               uint64 `json:"l1_blob_base_fee_default"`
 
+	// Upper limit values for gas oracle updates
+	L1BaseFeeLimit     uint64 `json:"l1_base_fee_limit"`
+	L1BlobBaseFeeLimit uint64 `json:"l1_blob_base_fee_limit"`
+
 	// L1BlobBaseFeeThreshold the threshold of L1 blob base fee to enter the default gas price mode
 	L1BlobBaseFeeThreshold uint64 `json:"l1_blob_base_fee_threshold"`
 }
```

### rollup/internal/controller/relayer/l1_relayer.go
```diff
@@ -173,6 +173,18 @@ func (r *Layer1Relayer) ProcessGasPriceOracle() {
 			} else if err != nil {
 				return
 			}
+			// Cap base fee update at the configured upper limit
+			if limit := r.cfg.GasOracleConfig.L1BaseFeeLimit; baseFee > limit {
+				log.Error("L1 base fee exceed max limit, set to max limit", "baseFee", baseFee, "maxLimit", limit)
+				r.metrics.rollupL1RelayerGasPriceOracleFeeOverLimitTotal.Inc()
+				baseFee = limit
+			}
+			// Cap blob base fee update at the configured upper limit
+			if limit := r.cfg.GasOracleConfig.L1BlobBaseFeeLimit; blobBaseFee > limit {
+				log.Error("L1 blob base fee exceed max limit, set to max limit", "blobBaseFee", blobBaseFee, "maxLimit", limit)
+				r.metrics.rollupL1RelayerGasPriceOracleFeeOverLimitTotal.Inc()
+				blobBaseFee = limit
+			}
 			data, err := r.l1GasOracleABI.Pack("setL1BaseFeeAndBlobBaseFee", new(big.Int).SetUint64(baseFee), new(big.Int).SetUint64(blobBaseFee))
 			if err != nil {
 				log.Error("Failed to pack setL1BaseFeeAndBlobBaseFee", "block.Hash", block.Hash, "block.Height", block.Number, "block.BaseFee", baseFee, "block.BlobBaseFee", blobBaseFee, "err", err)
```

### rollup/internal/controller/relayer/l1_relayer_metrics.go
```diff
@@ -8,11 +8,12 @@ import (
 )
 
 type l1RelayerMetrics struct {
-	rollupL1RelayerGasPriceOraclerRunTotal      prometheus.Counter
-	rollupL1RelayerLatestBaseFee                prometheus.Gauge
-	rollupL1RelayerLatestBlobBaseFee            prometheus.Gauge
-	rollupL1UpdateGasOracleConfirmedTotal       prometheus.Counter
-	rollupL1UpdateGasOracleConfirmedFailedTotal prometheus.Counter
+	rollupL1RelayerGasPriceOraclerRunTotal         prometheus.Counter
+	rollupL1RelayerLatestBaseFee                   prometheus.Gauge
+	rollupL1RelayerLatestBlobBaseFee               prometheus.Gauge
+	rollupL1UpdateGasOracleConfirmedTotal          prometheus.Counter
+	rollupL1UpdateGasOracleConfirmedFailedTotal    prometheus.Counter
+	rollupL1RelayerGasPriceOracleFeeOverLimitTotal prometheus.Counter
 }
 
 var (
@@ -43,6 +44,10 @@ func initL1RelayerMetrics(reg prometheus.Registerer) *l1RelayerMetrics {
 				Name: "rollup_layer1_update_gas_oracle_confirmed_failed_total",
 				Help: "The total number of updating layer1 gas oracle confirmed failed",
 			}),
+			rollupL1RelayerGasPriceOracleFeeOverLimitTotal: promauto.With(reg).NewCounter(prometheus.CounterOpts{
+				Name: "rollup_layer1_gas_price_oracle_fee_over_limit_total",
+				Help: "The total number of times when a gas price oracle fee update went over the configured limit",
+			}),
 		}
 	})
 	return l1RelayerMetric
```
