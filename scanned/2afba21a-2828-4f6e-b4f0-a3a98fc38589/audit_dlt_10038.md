# [?] Merge branch 'feat/testnet-fixes' into nodes-coordinator-underflow-fix

## Summary
Severity: Unknown
Chain: MultiversX
Component: multiversx/mx-chain-go
Published: 2026-07-09
Source: https://github.com/multiversx/mx-chain-go/commit/57bfb43227d8ab027c25c4e54a285ed988e933fb
Type: security-commit

## Details
Merge branch 'feat/testnet-fixes' into nodes-coordinator-underflow-fix

## Patch
### cmd/node/CLI.md
```diff
@@ -74,6 +74,7 @@ GLOBAL OPTIONS:
    --repopulate-tokens-supplies              Boolean flag for repopulating the tokens supplies database. It will delete the current data, iterate over the entire trie and add he new obtained supplies
    --p2p-prometheus-metrics                  Boolean option for enabling the /debug/metrics/prometheus route for p2p prometheus metrics
    --state-accesses-types-to-collect value   String slice option for enabling collecting specified state accesses types. Can be (READ, WRITE)
+   --print-prettified-header                 Boolean option for enabling the logging of prettified headers in consensus
    --help, -h                                show help
    --version, -v                             print the version
    
```

### cmd/node/config/config.toml
```diff
@@ -619,6 +619,12 @@
     Type = "SizeLRU"
     SizeInBytes = 52428800 # 50MB
 
+[QuarantinedHeadersCache]
+    Name = "QuarantinedHeadersCache"
+    Capacity = 100
+    Type = "SizeLRU"
+    SizeInBytes = 10485760 # 10MB
+
 [PostProcessTransactionsCache]
     Name = "PostProcessTransactionsCache"
     Capacity = 250000
```

### cmd/node/flags.go
```diff
@@ -416,6 +416,12 @@ var (
 		Name:  "state-accesses-types-to-collect",
 		Usage: "String slice option for enabling collecting specified state accesses types. Can be (READ, WRITE)",
 	}
+
+	// printPrettifiedHeader defines a flag for enabling prettified header logging
+	printPrettifiedHeader = cli.BoolFlag{
+		Name:  "print-prettified-header",
+		Usage: "Boolean option for enabling the logging of prettified headers in consensus",
+	}
 )
 
 func getFlags() []cli.Flag {
@@ -479,6 +485,7 @@ func getFlags() []cli.Flag {
 		repopulateTokensSupplies,
 		p2pPrometheusMetrics,
 		stateAccessesTypesToCollect,
+		printPrettifiedHeader,
 	}
 }
 
@@ -508,6 +515,7 @@ func getFlagsConfig(ctx *cli.Context, log logger.Logger) *config.ContextFlagsCon
 	flagsConfig.OperationMode = ctx.GlobalString(operationMode.Name)
 	flagsConfig.RepopulateTokensSupplies = ctx.GlobalBool(repopulateTokensSupplies.Name)
 	flagsConfig.P2PPrometheusMetricsEnabled = ctx.GlobalBool(p2pPrometheusMetrics.Name)
+	flagsConfig.PrintPrettifiedHeader = ctx.GlobalBool(printPrettifiedHeader.Name)
 
 	if ctx.GlobalBool(noKey.Name) {
 		log.Warn("the provided -no-key option is deprecated and will soon be removed. To start a node without " +
```

### common/common.go
```diff
@@ -302,6 +302,21 @@ func PrepareTimestampBasedOnHeaderData(headerTimestamp uint64, headerEpoch uint3
 	return timestampSec, timestampMs, nil
 }
 
+// LogPrettifiedHeader logs the prettified representation of the provided header or an error if prettification fails
+func LogPrettifiedHeader(header data.HeaderHandler, sentOrReceived string, version string, configsHandler CommonConfigsHandler) {
+	if !configsHandler.PrintPrettifiedHeader() {
+		return
+	}
+
+	headerOutput, err := PrettifyStruct(header)
+	message := fmt.Sprintf("Proposed header %s %s", sentOrReceived, version)
+	if err != nil {
+		log.Debug(message, "error", err)
+	} else {
+		log.Debug(message, "header", headerOutput)
+	}
+}
+
 // PrettifyStruct returns a JSON string representation of a struct, converting byte slices to hex
 // and formatting big number values into readable strings. Useful for logging or debugging.
 func PrettifyStruct(x interface{}) (string, error) {
```

### common/common_test.go
```diff
@@ -505,6 +505,34 @@ func TestPrettifyStruct(t *testing.T) {
 		t.Log("MetaBlock", prettified)
 
 	})
+
+	t.Run("with headers V3", func(t *testing.T) {
+		t.Parallel()
+
+		header := &block.HeaderV3{}
+		prettified, err := common.PrettifyStruct(header)
+		require.NoError(t, err)
+		t.Log("HeaderV3", prettified)
+
+		meta := &block.MetaBlockV3{}
+		prettified, err = common.PrettifyStruct(meta)
+		require.NoError(t, err)
+		t.Log("MetaBlockV3", prettified)
+	})
+
+	t.Run("with complete headers V3", func(t *testing.T) {
+		t.Parallel()
+
+		header := createMockShardHeaderV3()
+		prettified, err := common.PrettifyStruct(header)
+		require.NoError(t, err)
+		t.Log("HeaderV3", prettified)
+
+		meta := createMockMetaHeaderV3()
+		prettified, err = common.PrettifyStruct(meta)
+		require.NoError(t, err)
+		t.Log("MetaBlockV3", prettified)
+	})
 }
 
 func TestGetLastBaseExecutionResultHandler(t *testing.T) {
@@ -689,6 +717,184 @@ func TestPrepareLogEventsKey(t *testing.T) {
 	require.Equal(t, "logsLogsX", string(logs))
 }
 
+func createMockMetaHeaderV3() *block.MetaBlockV3 {
+	return &block.MetaBlockV3{
+		Nonce:           42,
+		Epoch:           2,
+		Round:           15,
+		TimestampMs:     123456789,
+		PrevHash:        []byte("prev_hash"),
+		PrevRandSeed:    []byte("prev_seed"),
+		RandSeed:        []byte("new_seed"),
+		ChainID:         []byte("chain-id"),
+		SoftwareVersion: []byte("v1.0.0"),
+		LeaderSignature: []byte("leader_signature"),
+
+		MiniBlockHeaders: []block.MiniBlockHeader{
+			{Hash: []byte("meta-to-s0"), SenderShardID: core.MetachainShardId, ReceiverShardID: 0},
+			{Hash: []byte("meta-to-s1"), SenderShardID: core.MetachainShardId, ReceiverShardID: 1},
+		},
+
+		ShardInfo: []block.ShardData{
+			{
+				ShardID:    0,
+				Round:      10,
+				Nonce:      41,
+				Epoch:      1,
+				HeaderHash: []byte("shard0-hash"),
+				ShardMiniBlockHeaders: []block.MiniBlockHeader{
+					{SenderShardID: 0, ReceiverShardID: 1, Hash: []byte("s0-to-s1")},
+				},
+			},
+			{
+				ShardID:    1,
+				Round:      11,
+				Nonce:      40,
+				Epoch:      1,
+				HeaderHash: []byte("shard1-hash"),
+				ShardMiniBlockHeaders: []block.MiniBlockHeader{
+					{SenderShardID: 1, ReceiverShardID: 0, Hash: []byte("s1-to-s0")},
+				},
+			},
+		},
+		ShardInfoProposal: []block.ShardDataProposal{
+			{ShardID: 0, HeaderHash: []byte("shard-0-hash"), Nonce: 41, Round: 10, Epoch: 1},
+			{ShardID: 1, HeaderHash: []byte("shard-1-hash"), Nonce: 40, Round: 11, Epoch: 1},
+		},
+		ExecutionResults: []*block.MetaExecutionResult{
+			{
+				ExecutionResult: &block.BaseMetaExecutionResult{
+					BaseExecutionResult: &block.BaseExecutionResult{
+						HeaderHash:  []byte("hdr-hash-10"),
+						HeaderNonce: 39,
+						HeaderRound: 10,
+						HeaderEpoch: 1,
+						RootHash:    []byte("root-hash-10"),
+					},
+					AccumulatedFeesInEpoch: big.NewInt(1000),
+					DevFeesInEpoch:         big.NewInt(100),
+					ValidatorStatsRootHash: []byte("validator-stats-root-hash"),
+				},
+				AccumulatedFees: big.NewInt(1000),
+				DeveloperFees:   big.NewInt(100),
+				ReceiptsHash:    []byte("receipts hash"),
+			},
+			{
+				ExecutionResult: &block.BaseMetaExecutionResult{
+					BaseExecutionResult: &block.BaseExecutionResult{
+						HeaderHash:  []byte("hdr-hash-11"),
+						HeaderNonce: 40,
+						HeaderRound: 11,
+						HeaderEpoch: 1,
+						RootHash:    []byte("root-hash-11"),
+					},
+					AccumulatedFeesInEpoch: big.NewInt(2000),
+					DevFeesInEpoch:         big.NewInt(200),
+					ValidatorStatsRootHash: []byte("validator-stats-root-hash-1"),
+				},
+				AccumulatedFees: big.NewInt(2000),
+				DeveloperFees:   big.NewInt(200),
+				ReceiptsHash:    []byte("receipts-hash-1"),
+			},
+			{
+				ExecutionResult: &block.BaseMetaExecutionResult{
+					BaseExecutionResult: &block.BaseExecutionResult{
+						HeaderHash:  []byte("hdr-hash-last"),
+						HeaderNonce: 41,
+						HeaderRound: 12,
+						HeaderEpoch: 2,
+						RootHash:    []byte("root-hash-last"),
+					},
+					AccumulatedFeesInEpoch: big.NewInt(3000),
+					DevFeesInEpoch:         big.NewInt(300),
+					ValidatorStatsRootHash: []byte("validator-stats-root-hash-2"),
+				},
+				AccumulatedFees: big.NewInt(3000),
+				DeveloperFees:   big.NewInt(300),
+				ReceiptsHash:    []byte("receipts-hash-2"),
+			},
+		},
+
+		LastExecutionResult: &block.MetaExecutionResultInfo{
+			NotarizedInRound: 14,
+			ExecutionResult: &block.BaseMetaExecutionResult{
+				BaseExecutionResult: &block.BaseExecutionResult{
+					HeaderHash:  []byte("hdr-hash-last"),
+					HeaderNonce: 41,
+					HeaderRound: 12,
+					HeaderEpoch: 2,
+					RootHash:    []byte("root-hash-last"),
+				},
+				AccumulatedFeesInEpoch: big.NewInt(3000),
+				DevFeesInEpoch:         big.NewInt(300),
+				ValidatorStatsRootHash: []byte("validator-stats-root-hash-2"),
+			},
+		},
+	}
+}
+
+func createMockShardHeaderV3() *block.HeaderV3 {
+	var hdrNonce = uint64(56)
+	var hdrRound = uint64(67)
+	var hdrEpoch = uint32(78)
+	return &block.HeaderV3{
+		Nonce:            hdrNonce,
+		PrevHash:         []byte("prev hash"),
+		PrevRandSeed:     []byte("prev rand seed"),
+		RandSeed:         []byte("rand seed"),
+		ShardID:          uint32(1),
+		TimestampMs:      0,
+		Round:            hdrRound,
+		Epoch:            hdrEpoch,
+		BlockBodyType:    block.TxBlock,
+		LeaderSignature:  []byte("signature"),
+		MiniBlockHeaders: nil,
+		PeerChanges:      nil,
+		MetaBlockHashes:  nil,
+		TxCount:          0,
+		ChainID:          []byte("chain ID"),
+		SoftwareVersion:  []byte("version"),
+		LastExecutionResult: &block.ExecutionResultInfo{
+			ExecutionResult: &block.BaseExecutionResult{
+				HeaderHash:  []byte("header hash"),
+				HeaderNonce: hdrNonce - 1,
+				HeaderRound: hdrRound - 1,
+				HeaderEpoch: hdrEpoch,
+				RootHash:    []byte("root hash"),
+			},
+			NotarizedInRound: hdrRound - 1,
+		},
+		ExecutionResults: []*block.ExecutionResult{
+			{
+				BaseExecutionResult: &block.BaseExecutionResult{
+					HeaderHash:  []byte("header hash"),
+					HeaderNonce: hdrNonce - 3,
+					HeaderRound: hdrRound - 3,
+					HeaderEpoch: hdrEpoch - 1,
+					RootHash:    []byte("root hash"),
+				},
+			},
+			{
+				BaseExecutionResult: &block.BaseExecutionResult{
+					HeaderHash:  []byte("header hash"),
+					HeaderNonce: hdrNonce - 2,
+					HeaderRound: hdrRound - 2,
+					HeaderEpoch: hdrEpoch - 1,
+					RootHash:    []byte("root hash"),
+				},
+			},
+			{
+				BaseExecutionResult: &block.BaseExecutionResult{
+					HeaderHash:  []byte("header hash"),
+					HeaderNonce: hdrNonce - 1,
+					HeaderRound: hdrRound - 1,
+					HeaderEpoch: hdrEpoch,
+					RootHash:    []byte("root hash"),
+				},
+			},
+		},
+	}
+}
 func TestGetMiniBlockHeadersFromExecResult(t *testing.T) {
 	t.Parallel()
 
```

### common/configs/commonConfigs.go
```diff
@@ -38,6 +38,7 @@ type commonConfigs struct {
 	orderedEpochStartConfigByRound []config.EpochStartConfigByRound
 	orderedConsensusConfigByEpoch  []config.ConsensusConfigByEpoch
 	orderedConsensusConfigByRound  []config.ConsensusConfigByRound
+	printPrettifiedHeader          bool
 }
 
 // NewCommonConfigsHandler creates a new process configs by epoch component
@@ -46,6 +47,7 @@ func NewCommonConfigsHandler(
 	configsByRound []config.EpochStartConfigByRound,
 	consensusConfigByEpoch []config.ConsensusConfigByEpoch,
 	consensusConfigByRound []config.ConsensusConfigByRound,
+	printPrettifiedHeader bool,
 ) (*commonConfigs, error) {
 	err := checkCommonConfigsByEpoch(configsByEpoch)
 	if err != nil {
@@ -71,6 +73,7 @@ func NewCommonConfigsHandler(
 		orderedEpochStartConfigByRound: make([]config.EpochStartConfigByRound, len(configsByRound)),
 		orderedConsensusConfigByEpoch:  make([]config.ConsensusConfigByEpoch, len(consensusConfigByEpoch)),
 		orderedConsensusConfigByRound:  make([]config.ConsensusConfigByRound, len(consensusConfigByRound)),
+		printPrettifiedHeader:          printPrettifiedHeader,
 	}
 
 	// sort the config values in ascending order
@@ -297,6 +300,11 @@ func (cc *commonConfigs) GetActiveTimingBoundaryRound(round uint64) uint64 {
 	return 0
 }
 
+// PrintPrettifiedHeader returns whether prettified headers should be logged
+func (cc *commonConfigs) PrintPrettifiedHeader() bool {
+	return cc.printPrettifiedHeader
+}
+
 // IsInterfaceNil checks if the instance is nil
 func (cc *commonConfigs) IsInterfaceNil() bool {
 	return cc == nil
```

### common/configs/commonConfigs_test.go
```diff
@@ -29,15 +29,15 @@ func TestNewCommonConfigsHandler(t *testing.T) {
 	t.Run("should return error for empty config by epoch", func(t *testing.T) {
 		t.Parallel()
 
-		pce, err := configs.NewCommonConfigsHandler(nil, []config.EpochStartConfigByRound{}, []config.ConsensusConfigByEpoch{}, defaultConsensusConfigsByRound())
+		pce, err := configs.NewCommonConfigsHandler(nil, []config.EpochStartConfigByRound{}, []config.ConsensusConfigByEpoch{}, defaultConsensusConfigsByRound(), false)
 		require.Nil(t, pce)
 		require.Equal(t, configs.ErrEmptyCommonConfigsByEpoch, err)
 	})
 
 	t.Run("should return error for empty config by round", func(t *testing.T) {
 		t.Parallel()
 
-		pce, err := configs.NewCommonConfigsHandler([]config.EpochStartConfigByEpoch{{EnableEpoch: 0}}, nil, []config.ConsensusConfigByEpoch{{EnableEpoch: 0}}, defaultConsensusConfigsByRound())
+		pce, err := configs.NewCommonConfigsHandler([]config.EpochStartConfigByEpoch{{EnableEpoch: 0}}, nil, []config.ConsensusConfigByEpoch{{EnableEpoch: 0}}, defaultConsensusConfigsByRound(), false)
 		require.Nil(t, pce)
 		require.Equal(t, configs.ErrEmptyCommonConfigsByRound, err)
 	})
@@ -49,7 +49,7 @@ func TestNewCommonConfigsHandler(t *testing.T) {
 			{EnableEpoch: 0, GracePeriodRounds: 1},
 			{EnableEpoch: 0, GracePeriodRounds: 2},
 		}
-		pce, err := configs.NewCommonConfigsHandler(conf, []config.EpochStartConfigByRound{}, []config.ConsensusConfigByEpoch{}, defaultConsensusConfigsByRound())
+		pce, err := configs.NewCommonConfigsHandler(conf, []config.EpochStartConfigByRound{}, []config.ConsensusConfigByEpoch{}, defaultConsensusConfigsByRound(), false)
 		require.Nil(t, pce)
 		require.Equal(t, configs.ErrDuplicatedEpochConfig, err)
 	})
@@ -61,7 +61,7 @@ func TestNewCommonConfigsHandler(t *testing.T) {
 			{EnableEpoch: 1, GracePeriodRounds: 1},
 			{EnableEpoch: 2, GracePeriodRounds: 2},
 		}
-		pce, err := configs.NewCommonConfigsHandler(conf, []config.EpochStartConfigByRound{}, []config.ConsensusConfigByEpoch{}, defaultConsensusConfigsByRound())
+		pce, err := configs.NewCommonConfigsHandler(conf, []config.EpochStartConfigByRound{}, []config.ConsensusConfigByEpoch{}, defaultConsensusConfigsByRound(), false)
 		require.Nil(t, pce)
 		require.Equal(t, configs.ErrMissingEpochZeroConfig, err)
 	})
@@ -74,6 +74,7 @@ func TestNewCommonConfigsHandler(t *testing.T) {
 			[]config.EpochStartConfigByRound{{EnableRound: 0}},
 			[]config.ConsensusConfigByEpoch{{EnableEpoch: 0}},
 			nil,
+			false,
 		)
 		require.Nil(t, pce)
 		require.Equal(t, configs.ErrEmptyConsensusConfigsByRound, err)
@@ -98,6 +99,7 @@ func TestNewCommonConfigsHandler(t *testing.T) {
 					ProcessingThresholdPercent: 85,
 				},
 			},
+			false,
 		)
 		require.Nil(t, pce)
 		require.Equal(t, configs.ErrMissingRoundZeroConfig, err)
@@ -120,6 +122,7 @@ func TestNewCommonConfigsHandler(t *testing.T) {
 				{EnableRound: 0, SubroundsTiming: validTiming, ProcessingThresholdPercent: 85},
 				{EnableRound: 0, SubroundsTiming: validTiming, ProcessingThresholdPercent: 85},
 			},
+			false,
 		)
 		require.Nil(t, pce)
 		require.Equal(t, configs.ErrDuplicatedRoundConfig, err)
@@ -142,7 +145,7 @@ func TestNewCommonConfigsHandler(t *testing.T) {
 			{EnableEpoch: 1, NumRoundsToWaitBeforeSignalingChronologyStuck: 11},
 		}
 
-		pce, err := configs.NewCommonConfigsHandler(conf, confByRound, consensusConf, defaultConsensusConfigsByRound())
+		pce, err := configs.NewCommonConfigsHandler(conf, confByRound, consensusConf, defaultConsensusConfigsByRound(), false)
 		require.NotNil(t, pce)
 		require.NoError(t, err)
 		require.False(t, pce.IsInterfaceNil())
@@ -198,7 +201,7 @@ func TestCommonConfigsByEpoch_Getters(t *testing.T) {
 	t.Run("get grace period rounds by epoch", func(t *testing.T) {
 		t.Parallel()
 
-		cc, _ := configs.NewCommonConfigsHandler(conf, confByRound, consensusConf, consensusConfByRound)
+		cc, _ := configs.NewCommonConfigsHandler(conf, confByRound, consensusConf, consensusConfByRound, false)
 
 		gracePeriodRounds := cc.GetGracePeriodRoundsByEpoch(0)
 		require.Equal(t, uint32(10), gracePeriodRounds)
@@ -210,7 +213,7 @@ func TestCommonConfigsByEpoch_Getters(t *testing.T) {
 	t.Run("get extra delay for request block info", func(t *testing.T) {
 		t.Parallel()
 
-		cc, _ := configs.NewCommonConfigsHandler(conf, confByRound, consensusConf, consensusConfByRound)
+		cc, _ := configs.NewCommonConfigsHandler(conf, confByRound, consensusConf, consensusConfByRound, false)
 
 		extraDelayForRequests := cc.GetExtraDelayForRequestBlockInfoInMs(0)
 		require.Equal(t, uint32(20), extraDelayForRequests)
@@ -222,7 +225,7 @@ func TestCommonConfigsByEpoch_Getters(t *testing.T) {
 	t.Run("get max rounds without committed start in epoch block by round", func(t *testing.T) {
 		t.Parallel()
 
-		cc, _ := configs.NewCommonConfigsHandler(conf, confByRound, consensusConf, consensusConfByRound)
+		cc, _ := configs.NewCommonConfigsHandler(conf, confByRound, consensusConf, consensusConfByRound, false)
 
 		maxRoundsWithoutCommitedStartInEpochBlock := cc.GetMaxRoundsWithoutCommittedStartInEpochBlockInRound(0)
 		require.Equal(t, uint32(30), maxRoundsWithoutCommitedStartInEpochBlock)
@@ -237,7 +240,7 @@ func TestCommonConfigsByEpoch_Getters(t *testing.T) {
 		// subround index constants mirroring bls.SrStartRound=0, SrBlock=1, SrSignature=2, SrEndRound=3
 		const srStartRound, srBlock, srSignature = 0, 1, 2
 
-		cc, _ := configs.NewCommonConfigsHandler(conf, confByRound, consensusConf, consensusConfByRound)
+		cc, _ := configs.NewCommonConfigsHandler(conf, confByRound, consensusConf, consensusConfByRound, false)
 
 		timing := cc.GetSubroundsTimingByRound(0)
 		require.Equal(t, consensusConfByRound[0].SubroundsTiming[srStartRound].EndTime, timing.SubroundsTiming[srStartRound].EndTime)
@@ -260,7 +263,7 @@ func TestCommonConfigsByEpoch_Getters(t *testing.T) {
 	t.Run("get active timing boundary round", func(t *testing.T) {
 		t.Parallel()
 
-		cc, _ := configs.NewCommonConfigsHandler(conf, confByRound, consensusConf, consensusConfByRound)
+		cc, _ := configs.NewCommonConfigsHandler(conf, confByRound, consensusConf, consensusConfByRound, false)
 
 		require.Equal(t, uint64(0), cc.GetActiveTimingBoundaryRound(0))
 		require.Equal(t, uint64(0), cc.GetActiveTimingBoundaryRound(9))
@@ -291,7 +294,7 @@ func TestCheckConsensusConfigsByRound(t *testing.T) {
 		t.Parallel()
 
 		cc, err := configs.NewCommonConfigsHandler(baseEpochConf, baseRoundConf, baseConsensusEpoch,
-			[]config.ConsensusConfigByRound{validConfig})
+			[]config.ConsensusConfigByRound{validConfig}, false)
 		require.NoError(t, err)
 		require.NotNil(t, cc)
 	})
@@ -310,7 +313,7 @@ func TestCheckConsensusConfigsByRound(t *testing.T) {
 			ProcessingThresholdPercent: 85,
 		}
 		_, err := configs.NewCommonConfigsHandler(baseEpochConf, baseRoundConf, baseConsensusEpoch,
-			[]config.ConsensusConfigByRound{bad})
+			[]config.ConsensusConfigByRound{bad}, false)
 		require.Equal(t, configs.ErrInvalidSubroundsTimingCount, err)
 	})
 
@@ -328,7 +331,7 @@ func TestCheckConsensusConfigsByRound(t *testing.T) {
 			ProcessingThresholdPercent: 85,
 		}
 		_, err := configs.NewCommonConfigsHandler(baseEpochConf, baseRoundConf, baseConsensusEpoch,
-			[]config.ConsensusConfigByRound{bad})
+			[]config.ConsensusConfigByRound{bad}, false)
 		require.Equal(t, configs.ErrNegativeSubroundTiming, err)
 	})
 
@@ -346,7 +349,7 @@ func TestCheckConsensusConfigsByRound(t *testing.T) {
 			ProcessingThresholdPercent: 85,
 		}
 		_, err := configs.NewCommonConfigsHandler(baseEpochConf, baseRoundConf, baseConsensusEpoch,
-			[]config.ConsensusConfigByRound{bad})
+			[]config.ConsensusConfigByRound{bad}, false)
 		require.Equal(t, configs.ErrInvalidSubroundTimingRange, err)
 	})
 
@@ -364,7 +367,7 @@ func TestCheckConsensusConfigsByRound(t *testing.T) {
 			ProcessingThresholdPercent: 85,
 		}
 		_, err := configs.NewCommonConfigsHandler(baseEpochConf, baseRoundConf, baseConsensusEpoch,
-			[]config.ConsensusConfigByRound{bad})
+			[]config.ConsensusConfigByRound{bad}, false)
 		require.Equal(t, configs.ErrOverlappingSubroundTiming, err)
 	})
 
@@ -382,7 +385,7 @@ func TestCheckConsensusConfigsByRound(t *testing.T) {
 			ProcessingThresholdPercent: 85,
 		}
 		_, err := configs.NewCommonConfigsHandler(baseEpochConf, baseRoundConf, baseConsensusEpoch,
-			[]config.ConsensusConfigByRound{bad})
+			[]config.ConsensusConfigByRound{bad}, false)
 		require.Equal(t, configs.ErrOverlappingSubroundTiming, err)
 	})
 
@@ -400,7 +403,7 @@ func TestCheckConsensusConfigsByRound(t *testing.T) {
 			ProcessingThresholdPercent: 85,
 		}
 		_, err := configs.NewCommonConfigsHandler(baseEpochConf, baseRoundConf, baseConsensusEpoch,
-			[]config.ConsensusConfigByRound{bad})
+			[]config.ConsensusConfigByRound{bad}, false)
 		require.Equal(t, configs.ErrSubroundTimingExceedsRound, err)
 	})
 
@@ -410,7 +413,7 @@ func TestCheckConsensusConfigsByRound(t *testing.T) {
 		bad := validConfig
 		bad.ProcessingThresholdPercent = 0
 		_, err := configs.NewCommonConfigsHandler(baseEpochConf, baseRoundConf, baseConsensusEpoch,
-			[]config.ConsensusConfigByRound{bad})
+			[]config.ConsensusConfigByRound{bad}, false)
 		require.Equal(t, configs.ErrInvalidProcessingThreshold, err)
 	})
 
@@ -420,7 +423,7 @@ func TestCheckConsensusConfigsByRound(t *testing.T) {
 		bad := validConfig
 		bad.ProcessingThresholdPercent = 101
 		_, err := configs.NewCommonConfigsHandler(baseEpochConf, baseRoundConf, baseConsensusEpoch,
-			[]config.ConsensusConfigByRound{bad})
+			[]config.ConsensusConfigByRound{bad}, false)
 		require.Equal(t, configs.ErrInvalidProcessingThreshold, err)
 	})
 }
```

### common/interface.go
```diff
@@ -510,6 +510,7 @@ type CommonConfigsHandler interface {
 	GetNumRoundsToWaitBeforeSignalingChronologyStuck(epoch uint32) uint32
 	GetSubroundsTimingByRound(round uint64) config.ConsensusConfigByRound
 	GetActiveTimingBoundaryRound(round uint64) uint64
+	PrintPrettifiedHeader() bool
 
 	IsInterfaceNil() bool
 }
```

### config/config.go
```diff
@@ -227,6 +227,7 @@ type Config struct {
 	SmartContractDataPool        CacheConfig
 	ValidatorInfoPool            CacheConfig
 	ExecutedMiniBlocksCache      CacheConfig
+	QuarantinedHeadersCache      CacheConfig
 	PostProcessTransactionsCache CacheConfig
 	HeaderBodyCacheConfig        HeaderBodyCacheConfig
 	TrieSyncStorage              TrieSyncStorageConfig
```

### config/contextFlagsConfig.go
```diff
@@ -28,6 +28,7 @@ type ContextFlagsConfig struct {
 	OperationMode                string
 	RepopulateTokensSupplies     bool
 	P2PPrometheusMetricsEnabled  bool
+	PrintPrettifiedHeader        bool
 }
 
 // ImportDbConfig will hold the import-db parameters
```

### consensus/spos/bls/proxy/subroundsHandler.go
```diff
@@ -27,7 +27,6 @@ type SubroundsHandlerArgs struct {
 	OutportHandler       outport.OutportHandler
 	SentSignatureTracker spos.SentSignaturesTracker
 	EnableEpochsHandler  core.EnableEpochsHandler
-	CommonConfigsHandler common.CommonConfigsHandler
 	ChainID              []byte
 	CurrentPid           core.PeerID
 }
@@ -52,7 +51,6 @@ type SubroundsHandler struct {
 	outportHandler       outport.OutportHandler
 	sentSignatureTracker spos.SentSignaturesTracker
 	enableEpochsHandler  core.EnableEpochsHandler
-	commonConfigsHandler common.CommonConfigsHandler
 	chainID              []byte
 	currentPid           core.PeerID
 	currentConsensusType consensusStateMachineType
@@ -89,7 +87,6 @@ func NewSubroundsHandler(args *SubroundsHandlerArgs) (*SubroundsHandler, error)
 		outportHandler:       args.OutportHandler,
 		sentSignatureTracker: args.SentSignatureTracker,
 		enableEpochsHandler:  args.EnableEpochsHandler,
-		commonConfigsHandler: args.CommonConfigsHandler,
 		chainID:              args.ChainID,
 		currentPid:           args.CurrentPid,
 		currentConsensusType: consensusNone,
@@ -128,9 +125,6 @@ func checkArgs(args *SubroundsHandlerArgs) error {
 	if check.IfNil(args.EnableEpochsHandler) {
 		return ErrNilEnableEpochsHandler
 	}
-	if check.IfNil(args.CommonConfigsHandler) {
-		return common.ErrNilCommonConfigsHandler
-	}
 	if args.ChainID == nil {
 		return ErrNilChainID
 	}
@@ -188,7 +182,6 @@ func (s *SubroundsHandler) generateSubroundsForCurrentType(epoch uint32) error {
 			s.sentSignatureTracker,
 			s.signatureThrottler,
 			s.outportHandler,
-			s.commonConfigsHandler,
 		)
 	} else {
 		fct, err = v1.NewSubroundsFactory(
@@ -200,7 +193,6 @@ func (s *SubroundsHandler) generateSubroundsForCurrentType(epoch uint32) error {
 			s.appStatusHandler,
 			s.sentSignatureTracker,
 			s.outportHandler,
-			s.commonConfigsHandler,
 		)
 	}
 	if err != nil {
```

### consensus/spos/bls/proxy/subroundsHandler_test.go
```diff
@@ -51,7 +51,6 @@ func getDefaultArgumentsSubroundHandler() (*SubroundsHandlerArgs, *spos.Consensu
 		OutportHandler:       &outportStub.OutportStub{},
 		SentSignatureTracker: &testscommon.SentSignatureTrackerStub{},
 		EnableEpochsHandler:  epochsEnable,
-		CommonConfigsHandler: testscommon.GetDefaultCommonConfigsHandler(),
 		ChainID:              []byte("chainID"),
 		CurrentPid:           "peerID",
 	}
@@ -93,6 +92,7 @@ func getDefaultArgumentsSubroundHandler() (*SubroundsHandlerArgs, *spos.Consensu
 
 	messagesHandler, _ := bls.NewConsensusService()
 	consensusCore.SetMessagesHandler(messagesHandler)
+	consensusCore.SetCommonConfigsHandler(testscommon.GetDefaultCommonConfigsHandler())
 
 	handlerArgs.ConsensusCoreHandler = consensusCore
 
```
