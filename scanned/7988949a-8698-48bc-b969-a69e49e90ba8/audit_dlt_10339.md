# [?] Fix race condition in gas-price oracle startup (#283)

## Summary
Severity: Unknown
Chain: Sonic
Component: 0xsoniclabs/sonic
Published: 2024-11-06
Source: https://github.com/0xsoniclabs/sonic/commit/4b981a46809fb0d41fe49600a4e0b89e1ce25820
Type: security-commit

## Details
Fix race condition in gas-price oracle startup (#283)

## Patch
### gossip/evm_state_reader.go
```diff
@@ -23,14 +23,6 @@ type EvmStateReader struct {
 	gpo   *gasprice.Oracle
 }
 
-func (s *Service) GetEvmStateReader() *EvmStateReader {
-	return &EvmStateReader{
-		ServiceFeed: &s.feed,
-		store:       s.store,
-		gpo:         s.gpo,
-	}
-}
-
 // MinGasPrice returns current hard lower bound for gas price
 func (r *EvmStateReader) MinGasPrice() *big.Int {
 	return r.store.GetRules().Economy.MinGasPrice
```

### gossip/gasprice/gasprice.go
```diff
@@ -106,20 +106,20 @@ func sanitizeBigInt(val, min, max, _default *big.Int, name string) *big.Int {
 
 // NewOracle returns a new gasprice oracle which can recommend suitable
 // gasprice for newly created transaction.
-func NewOracle(params Config) *Oracle {
+func NewOracle(params Config, backend Reader) *Oracle {
 	params.MaxGasPrice = sanitizeBigInt(params.MaxGasPrice, nil, nil, DefaultMaxGasPrice, "MaxGasPrice")
 	params.MinGasPrice = sanitizeBigInt(params.MinGasPrice, nil, nil, new(big.Int), "MinGasPrice")
 	params.DefaultCertainty = sanitizeBigInt(new(big.Int).SetUint64(params.DefaultCertainty), big.NewInt(0), DecimalUnitBn, big.NewInt(DecimalUnit/2), "DefaultCertainty").Uint64()
 	tCache, _ := lru.New(100)
 	return &Oracle{
-		cfg:    params,
-		tCache: tCache,
-		quit:   make(chan struct{}),
+		cfg:     params,
+		tCache:  tCache,
+		quit:    make(chan struct{}),
+		backend: backend,
 	}
 }
 
-func (gpo *Oracle) Start(backend Reader) {
-	gpo.backend = backend
+func (gpo *Oracle) Start() {
 	gpo.wg.Add(1)
 	go func() {
 		defer gpo.wg.Done()
```

### gossip/gasprice/gasprice_test.go
```diff
@@ -70,7 +70,7 @@ func TestOracle_EffectiveMinGasPrice(t *testing.T) {
 		pendingRules:      opera.FakeNetRules(),
 	}
 
-	gpo := NewOracle(Config{})
+	gpo := NewOracle(Config{}, nil)
 	gpo.cfg.MaxGasPrice = math.MaxBig256
 	gpo.cfg.MinGasPrice = new(big.Int)
 
@@ -130,8 +130,7 @@ func TestOracle_constructiveGasPrice(t *testing.T) {
 		pendingRules:      opera.FakeNetRules(),
 	}
 
-	gpo := NewOracle(Config{})
-	gpo.backend = backend
+	gpo := NewOracle(Config{}, backend)
 	gpo.cfg.MaxGasPrice = math.MaxBig256
 	gpo.cfg.MinGasPrice = new(big.Int)
 
@@ -172,8 +171,7 @@ func TestOracle_reactiveGasPrice(t *testing.T) {
 		pendingRules:      opera.FakeNetRules(),
 	}
 
-	gpo := NewOracle(Config{})
-	gpo.backend = backend
+	gpo := NewOracle(Config{}, backend)
 	gpo.cfg.MaxGasPrice = math.MaxBig256
 	gpo.cfg.MinGasPrice = new(big.Int)
 
```

### gossip/service.go
```diff
@@ -209,9 +209,6 @@ func newService(config Config, store *Store, blockProc BlockProc, engine lachesi
 	netVerStore.GetNetworkVersion()
 	netVerStore.GetMissedVersion()
 
-	// create GPO
-	svc.gpo = gasprice.NewOracle(svc.config.GPO)
-
 	// create checkers
 	net := store.GetRules()
 	txSigner := gsignercache.Wrap(types.LatestSignerForChainID(new(big.Int).SetUint64(net.NetworkID)))
@@ -221,9 +218,16 @@ func newService(config Config, store *Store, blockProc BlockProc, engine lachesi
 	svc.checkers = makeCheckers(config.HeavyCheck, txSigner, &svc.heavyCheckReader, &svc.gasPowerCheckReader, svc.store)
 
 	// create tx pool
-	stateReader := svc.GetEvmStateReader()
+	stateReader := &EvmStateReader{
+		ServiceFeed: &svc.feed,
+		store:       svc.store,
+	}
 	svc.txpool = newTxPool(stateReader)
 
+	// create GPO
+	svc.gpo = gasprice.NewOracle(svc.config.GPO, &GPOBackend{svc.store, svc.txpool})
+	stateReader.gpo = svc.gpo
+
 	// init dialCandidates
 	dnsclient := dnsdisc.NewClient(dnsdisc.Config{})
 	var err error
@@ -417,7 +421,7 @@ func (s *Service) APIs() []rpc.API {
 
 // Start method invoked when the node is ready to start the service.
 func (s *Service) Start() error {
-	s.gpo.Start(&GPOBackend{s.store, s.txpool})
+	s.gpo.Start()
 	// start tflusher before starting snapshots generation
 	s.tflusher.Start()
 	blockState := s.store.GetBlockState()
```
