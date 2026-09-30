# [?] core/beacon: prevent invalid logsBloom length panic (#24946)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2022-05-31
Source: https://github.com/ethereum/go-ethereum/commit/8c0c0434c9aaad988b84b7a842e28fca69b2724d
Type: security-commit

## Details
core/beacon: prevent invalid logsBloom length panic (#24946)

* core/beacon: prevent invalid logsBloom length panic

* core/beacon: prevent negative baseFeePerGas

* Update core/beacon/types.go

Co-authored-by: Martin Holst Swende <martin@swende.se>

* eth/catalys: go format

Co-authored-by: Martin Holst Swende <martin@swende.se>

## Patch
### core/beacon/types.go
```diff
@@ -148,6 +148,13 @@ func ExecutableDataToBlock(params ExecutableDataV1) (*types.Block, error) {
 	if len(params.ExtraData) > 32 {
 		return nil, fmt.Errorf("invalid extradata length: %v", len(params.ExtraData))
 	}
+	if len(params.LogsBloom) != 256 {
+		return nil, fmt.Errorf("invalid logsBloom length: %v", len(params.LogsBloom))
+	}
+	// Check that baseFeePerGas is not negative or too big
+	if params.BaseFeePerGas != nil && (params.BaseFeePerGas.Sign() == -1 || params.BaseFeePerGas.BitLen() > 256) {
+		return nil, fmt.Errorf("invalid baseFeePerGas: %v", params.BaseFeePerGas)
+	}
 	header := &types.Header{
 		ParentHash:  params.ParentHash,
 		UncleHash:   types.EmptyUncleHash,
```

### eth/catalyst/api_test.go
```diff
@@ -787,6 +787,30 @@ func TestTrickRemoteBlockCache(t *testing.T) {
 	}
 }
 
+func TestInvalidBloom(t *testing.T) {
+	genesis, preMergeBlocks := generatePreMergeChain(10)
+	n, ethservice := startEthService(t, genesis, preMergeBlocks)
+	ethservice.Merger().ReachTTD()
+	defer n.Close()
+
+	commonAncestor := ethservice.BlockChain().CurrentBlock()
+	api := NewConsensusAPI(ethservice)
+
+	// Setup 10 blocks on the canonical chain
+	setupBlocks(t, ethservice, 10, commonAncestor, func(parent *types.Block) {})
+
+	// (1) check LatestValidHash by sending a normal payload (P1'')
+	payload := getNewPayload(t, api, commonAncestor)
+	payload.LogsBloom = append(payload.LogsBloom, byte(1))
+	status, err := api.NewPayloadV1(*payload)
+	if err != nil {
+		t.Fatal(err)
+	}
+	if status.Status != beacon.INVALIDBLOCKHASH {
+		t.Errorf("invalid status: expected VALID got: %v", status.Status)
+	}
+}
+
 func TestNewPayloadOnInvalidTerminalBlock(t *testing.T) {
 	genesis, preMergeBlocks := generatePreMergeChain(100)
 	fmt.Println(genesis.Config.TerminalTotalDifficulty)
```
