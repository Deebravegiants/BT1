# [?] fix: validate allocations locked amount in genesis to prevent panic (#3941)

## Summary
Severity: Unknown
Chain: Avalanche
Component: ava-labs/avalanchego
Published: 2025-05-07
Source: https://github.com/ava-labs/avalanchego/commit/7d44651f099b08a08ecee54535615df95bf22666
Type: security-commit

## Details
fix: validate allocations locked amount in genesis to prevent panic (#3941)

## Patch
### genesis/genesis.go
```diff
@@ -46,6 +46,7 @@ var (
 	errFutureStartTime                 = errors.New("startTime cannot be in the future")
 	errInitialStakeDurationTooLow      = errors.New("initial stake duration is too low")
 	errOverridesStandardNetworkConfig  = errors.New("overrides standard network genesis config")
+	errAllocationsLockedAmountTooLow   = errors.New("total allocations locked amount is too low")
 )
 
 // validateInitialStakedFunds ensures all staked
@@ -113,6 +114,27 @@ func validateInitialStakedFunds(config *Config) error {
 	return nil
 }
 
+// validateAllocationsLockedAmount ensures that the sum of all locked
+// allocation amounts is at least the number of initial stakers.
+func validateAllocationsLockedAmount(config *Config) error {
+	totalLocked := uint64(0)
+	for _, allocation := range config.Allocations {
+		for _, unlock := range allocation.UnlockSchedule {
+			totalLocked += unlock.Amount
+		}
+	}
+	stakersCount := len(config.InitialStakers)
+	if totalLocked < uint64(stakersCount) {
+		return fmt.Errorf(
+			"%w: %d locked < %d stakers",
+			errAllocationsLockedAmountTooLow,
+			totalLocked,
+			stakersCount,
+		)
+	}
+	return nil
+}
+
 // validateConfig returns an error if the provided
 // *Config is not considered valid.
 func validateConfig(networkID uint32, config *Config, stakingCfg *StakingConfig) error {
@@ -173,6 +195,10 @@ func validateConfig(networkID uint32, config *Config, stakingCfg *StakingConfig)
 		return fmt.Errorf("initial staked funds validation failed: %w", err)
 	}
 
+	if err := validateAllocationsLockedAmount(config); err != nil {
+		return err
+	}
+
 	if len(config.CChainGenesis) == 0 {
 		return errNoCChainGenesis
 	}
```

### genesis/genesis_test.go
```diff
@@ -33,6 +33,9 @@ var (
 		"networkID": 9999}}}}
 	}`)
 
+	//go:embed genesis_test_invalid_allocations.json
+	customGenesisConfigInvalidAllocationsJSON []byte
+
 	genesisStakingCfg = &StakingConfig{
 		MaxStakeDuration: 365 * 24 * time.Hour,
 	}
@@ -227,6 +230,11 @@ func TestGenesisFromFile(t *testing.T) {
 			missingFilepath: "missing.json",
 			expectedErr:     os.ErrNotExist,
 		},
+		"custom (locked allocations amount too low)": {
+			networkID:    9999,
+			customConfig: customGenesisConfigInvalidAllocationsJSON,
+			expectedErr:  errAllocationsLockedAmountTooLow,
+		},
 	}
 
 	for name, test := range tests {
```

### genesis/genesis_test_invalid_allocations.json
```diff
@@ -0,0 +1,40 @@
+{
+  "networkID": 9999,
+  "allocations": [
+    {
+      "ethAddr": "0x46a9c04f4bf783aa69daabd519dcf36978168b66",
+      "avaxAddr": "X-custom1g65uqn6t77p656w64023nh8nd9updzmxwd59gh",
+      "initialAmount": 22,
+      "unlockSchedule": [
+        {
+          "amount": 2,
+          "unlockTime": 1660987200
+        }
+      ]
+    }
+  ],
+  "startTime": 1660987200,
+  "initialStakeDuration": 31536000,
+  "initialStakedFunds": [
+    "X-custom1g65uqn6t77p656w64023nh8nd9updzmxwd59gh"
+  ],
+  "initialStakers": [
+    {
+      "nodeID": "NodeID-7gX65ndj8b6UA7uMp4vjQq3FcaC6aqY3Z",
+      "rewardAddress": "X-custom18jma8ppw3nhx5r4ap8clazz0dps7rv5u9xde7p",
+      "delegationFee": 5000
+    },
+    {
+      "nodeID": "NodeID-BW6UnRcxVBvFB4LTfdt8BpBaaw4Vt7ZeR",
+      "rewardAddress": "X-custom18jma8ppw3nhx5r4ap8clazz0dps7rv5u9xde7p",
+      "delegationFee": 5001
+    },
+    {
+      "nodeID": "NodeID-NAyhSLKgrm4Bxd49e5dUwooDDdrStRaj5",
+      "rewardAddress": "X-custom18jma8ppw3nhx5r4ap8clazz0dps7rv5u9xde7p",
+      "delegationFee": 5002
+    }
+  ],
+  "cChainGenesis": "{\"config\":{\"chainId\":43112}}",
+  "message": ""
+}
```
