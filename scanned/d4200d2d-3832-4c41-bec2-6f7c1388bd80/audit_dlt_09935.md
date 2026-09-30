# [?] load panic mitigation

## Summary
Severity: Unknown
Chain: Kaia
Component: kaiachain/kaia
Published: 2023-01-25
Source: https://github.com/kaiachain/kaia/commit/c90f185afb944c8c49bc7fcf14b2824dc7211b16
Type: security-commit

## Details
load panic mitigation

## Patch
### governance/api_test.go
```diff
@@ -174,6 +174,10 @@ func (bc *testBlockChain) Config() *params.ChainConfig {
 	return bc.config
 }
 
+func (bc *testBlockChain) CurrentBlock() *types.Block {
+	return types.NewBlock(bc.CurrentHeader(), nil, nil)
+}
+
 func (bc *testBlockChain) CurrentHeader() *types.Header {
 	return &types.Header{
 		Number: new(big.Int).SetUint64(bc.num),
```

### governance/contract.go
```diff
@@ -70,7 +70,7 @@ func (e *ContractEngine) UpdateParams() error {
 	}
 
 	// request the parameters required for generating the next block
-	head := chain.CurrentHeader().Number.Uint64()
+	head := chain.CurrentBlock().NumberU64()
 	pset, err := e.contractGetAllParamsAt(head + 1)
 	if err != nil {
 		return err
```

### governance/contract_connector.go
```diff
@@ -108,7 +108,7 @@ func (c *contractCaller) makeTx(contractAbi abi.ABI, fn string, args ...interfac
 // Make contract execution transaction
 func (c *contractCaller) makeEVM(tx *types.Transaction) (*vm.EVM, error) {
 	// Load the latest state
-	block := c.chain.GetBlockByNumber(c.chain.CurrentHeader().Number.Uint64())
+	block := c.chain.GetBlockByNumber(c.chain.CurrentBlock().NumberU64())
 	if block == nil {
 		logger.Error("Could not find the latest block", "num", c.chain.CurrentHeader().Number.Uint64())
 		return nil, errors.New("no block")
```

### governance/interface.go
```diff
@@ -107,6 +107,7 @@ type blockChain interface {
 	blockchain.ChainContext
 
 	CurrentHeader() *types.Header
+	CurrentBlock() *types.Block
 	GetHeaderByNumber(val uint64) *types.Header
 	GetBlockByNumber(num uint64) *types.Block
 	StateAt(root common.Hash) (*state.StateDB, error)
```

### governance/mixed.go
```diff
@@ -149,7 +149,7 @@ func (e *MixedEngine) UpdateParams() error {
 	// in this case, fall back to num=zero
 	num := big.NewInt(0)
 	if e.blockchain != nil {
-		num = e.blockchain.CurrentHeader().Number
+		num = e.blockchain.CurrentBlock().Number()
 	}
 
 	var contractParams *params.GovParamSet
```
