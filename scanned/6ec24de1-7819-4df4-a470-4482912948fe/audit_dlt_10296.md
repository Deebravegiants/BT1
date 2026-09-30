# [?] Fix race condition in TestValidatorSetHandling  (#937)

## Summary
Severity: Unknown
Chain: Rollkit
Component: evstack/ev-node
Published: 2023-05-16
Source: https://github.com/evstack/ev-node/commit/27fd84cea8fce85f5f86d692cd6013f14063d884
Type: security-commit

## Details
Fix race condition in TestValidatorSetHandling  (#937)

Closes: #938

## Patch
### node/full_client_test.go
```diff
@@ -650,7 +650,7 @@ func TestBlockchainInfo(t *testing.T) {
 	}
 }
 
-func createGenesisValidators(numNodes int, appCreator func(require *require.Assertions, vKeyToRemove tmcrypto.PrivKey, waitCh chan interface{}) *mocks.Application, require *require.Assertions, waitCh chan interface{}) *FullClient {
+func createGenesisValidators(numNodes int, appCreator func(require *require.Assertions, vKeyToRemove tmcrypto.PrivKey, wg *sync.WaitGroup) *mocks.Application, require *require.Assertions, wg *sync.WaitGroup) *FullClient {
 	vKeys := make([]tmcrypto.PrivKey, numNodes)
 	apps := make([]*mocks.Application, numNodes)
 	nodes := make([]*FullNode, numNodes)
@@ -659,7 +659,8 @@ func createGenesisValidators(numNodes int, appCreator func(require *require.Asse
 	for i := 0; i < len(vKeys); i++ {
 		vKeys[i] = ed25519.GenPrivKey()
 		genesisValidators[i] = tmtypes.GenesisValidator{Address: vKeys[i].PubKey().Address(), PubKey: vKeys[i].PubKey(), Power: int64(i + 100), Name: fmt.Sprintf("gen #%d", i)}
-		apps[i] = appCreator(require, vKeys[0], waitCh)
+		apps[i] = appCreator(require, vKeys[0], wg)
+		wg.Add(1)
 	}
 
 	dalc := &mockda.DataAvailabilityLayerClient{}
@@ -728,7 +729,7 @@ func checkValSetLatest(rpc *FullClient, assert *assert.Assertions, lastBlockHeig
 	assert.GreaterOrEqual(vals.BlockHeight, lastBlockHeight)
 }
 
-func createApp(require *require.Assertions, vKeyToRemove tmcrypto.PrivKey, waitCh chan interface{}) *mocks.Application {
+func createApp(require *require.Assertions, vKeyToRemove tmcrypto.PrivKey, wg *sync.WaitGroup) *mocks.Application {
 	app := &mocks.Application{}
 	app.On("InitChain", mock.Anything).Return(abci.ResponseInitChain{})
 	app.On("CheckTx", mock.Anything).Return(abci.ResponseCheckTx{})
@@ -744,9 +745,11 @@ func createApp(require *require.Assertions, vKeyToRemove tmcrypto.PrivKey, waitC
 	app.On("EndBlock", mock.Anything).Return(abci.ResponseEndBlock{ValidatorUpdates: []abci.ValidatorUpdate{{PubKey: pbValKey, Power: 0}}}).Once()
 	app.On("EndBlock", mock.Anything).Return(abci.ResponseEndBlock{}).Once()
 	app.On("EndBlock", mock.Anything).Return(abci.ResponseEndBlock{ValidatorUpdates: []abci.ValidatorUpdate{{PubKey: pbValKey, Power: 100}}}).Once()
+	app.On("EndBlock", mock.Anything).Return(abci.ResponseEndBlock{}).Times(5)
 	app.On("EndBlock", mock.Anything).Return(abci.ResponseEndBlock{}).Run(func(args mock.Arguments) {
-		waitCh <- nil
-	})
+		wg.Done()
+	}).Once()
+	app.On("EndBlock", mock.Anything).Return(abci.ResponseEndBlock{})
 	return app
 }
 
@@ -755,13 +758,12 @@ func TestValidatorSetHandling(t *testing.T) {
 	assert := assert.New(t)
 	require := require.New(t)
 
-	waitCh := make(chan interface{})
+	var wg sync.WaitGroup
 
 	numNodes := 2
-	rpc := createGenesisValidators(numNodes, createApp, require, waitCh)
+	rpc := createGenesisValidators(numNodes, createApp, require, &wg)
 
-	<-waitCh
-	<-waitCh
+	wg.Wait()
 
 	// test first blocks
 	for h := int64(1); h <= 3; h++ {
@@ -775,8 +777,6 @@ func TestValidatorSetHandling(t *testing.T) {
 
 	// 5th EndBlock adds validator back
 	for h := int64(6); h <= 9; h++ {
-		<-waitCh
-		<-waitCh
 		checkValSet(rpc, assert, h, numNodes)
 	}
 
@@ -789,11 +789,13 @@ func TestValidatorSetHandlingBased(t *testing.T) {
 	assert := assert.New(t)
 	require := require.New(t)
 
-	waitCh := make(chan interface{})
+	var wg sync.WaitGroup
 	numNodes := 1
-	rpc := createGenesisValidators(numNodes, createApp, require, waitCh)
+	rpc := createGenesisValidators(numNodes, createApp, require, &wg)
+
+	wg.Wait()
 
-	<-waitCh
+	time.Sleep(100 * time.Millisecond)
 
 	// test first blocks
 	for h := int64(1); h <= 3; h++ {
@@ -802,12 +804,10 @@ func TestValidatorSetHandlingBased(t *testing.T) {
 
 	// 3rd EndBlock removes the first validator and makes the rollup based
 	for h := int64(4); h <= 9; h++ {
-		<-waitCh
 		checkValSet(rpc, assert, h, numNodes-1)
 	}
 
 	// check for "latest block"
-	<-waitCh
 	checkValSetLatest(rpc, assert, 9, numNodes-1)
 }
 
```
