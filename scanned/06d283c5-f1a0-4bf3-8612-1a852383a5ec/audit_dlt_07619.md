# [?] consensus/clique: prevent 0 len extradata from panicing (#23538)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2021-09-21
Source: https://github.com/ethereum/go-ethereum/commit/b61ef24ccef9b4d14f4f3c97298fa6d4c1b6b47d
Type: security-commit

## Details
consensus/clique: prevent 0 len extradata from panicing (#23538)

Closes #23522

Co-authored-by: Martin Holst Swende <martin@swende.se>

## Patch
### core/genesis.go
```diff
@@ -310,7 +310,7 @@ func (g *Genesis) ToBlock(db ethdb.Database) *types.Block {
 func (g *Genesis) Commit(db ethdb.Database) (*types.Block, error) {
 	block := g.ToBlock(db)
 	if block.Number().Sign() != 0 {
-		return nil, fmt.Errorf("can't commit genesis block with number > 0")
+		return nil, errors.New("can't commit genesis block with number > 0")
 	}
 	config := g.Config
 	if config == nil {
@@ -319,6 +319,9 @@ func (g *Genesis) Commit(db ethdb.Database) (*types.Block, error) {
 	if err := config.CheckConfigForkOrder(); err != nil {
 		return nil, err
 	}
+	if config.Clique != nil && len(block.Extra()) == 0 {
+		return nil, errors.New("can't start clique chain without signers")
+	}
 	rawdb.WriteTd(db, block.Hash(), block.NumberU64(), g.Difficulty)
 	rawdb.WriteBlock(db, block)
 	rawdb.WriteReceipts(db, block.Hash(), block.NumberU64(), nil)
```

### core/genesis_test.go
```diff
@@ -39,6 +39,22 @@ func TestDefaultGenesisBlock(t *testing.T) {
 	if block.Hash() != params.RopstenGenesisHash {
 		t.Errorf("wrong ropsten genesis hash, got %v, want %v", block.Hash(), params.RopstenGenesisHash)
 	}
+	block = DefaultRinkebyGenesisBlock().ToBlock(nil)
+	if block.Hash() != params.RinkebyGenesisHash {
+		t.Errorf("wrong rinkeby genesis hash, got %v, want %v", block.Hash(), params.RinkebyGenesisHash)
+	}
+	block = DefaultGoerliGenesisBlock().ToBlock(nil)
+	if block.Hash() != params.GoerliGenesisHash {
+		t.Errorf("wrong goerli genesis hash, got %v, want %v", block.Hash(), params.GoerliGenesisHash)
+	}
+}
+
+func TestInvalidCliqueConfig(t *testing.T) {
+	block := DefaultGoerliGenesisBlock()
+	block.ExtraData = []byte{}
+	if _, err := block.Commit(nil); err == nil {
+		t.Fatal("Expected error on invalid clique config")
+	}
 }
 
 func TestSetupGenesis(t *testing.T) {
```

### miner/worker_test.go
```diff
@@ -74,8 +74,10 @@ var (
 func init() {
 	testTxPoolConfig = core.DefaultTxPoolConfig
 	testTxPoolConfig.Journal = ""
-	ethashChainConfig = params.TestChainConfig
-	cliqueChainConfig = params.TestChainConfig
+	ethashChainConfig = new(params.ChainConfig)
+	*ethashChainConfig = *params.TestChainConfig
+	cliqueChainConfig = new(params.ChainConfig)
+	*cliqueChainConfig = *params.TestChainConfig
 	cliqueChainConfig.Clique = &params.CliqueConfig{
 		Period: 10,
 		Epoch:  30000,
```
