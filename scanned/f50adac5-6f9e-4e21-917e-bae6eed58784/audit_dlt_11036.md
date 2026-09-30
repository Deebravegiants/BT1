# [?] core/vm, params: ensure order of forks, prevent overflow (#29023)

## Summary
Severity: Unknown
Chain: Optimism
Component: ethereum-optimism/op-geth
Published: 2024-04-08
Source: https://github.com/ethereum-optimism/op-geth/commit/1c12cf9b069f2b7c66a5575a331821ae682e23ab
Type: security-commit

## Details
core/vm, params: ensure order of forks, prevent overflow (#29023)

This PR fixes an overflow which can could happen if inconsistent blockchain rules were configured. Additionally, it tries to prevent such inconsistencies from occurring by making sure that merge cannot be enabled unless previous fork(s) are also enabled.

## Patch
### core/vm/operations_acl.go
```diff
@@ -187,7 +187,12 @@ func makeCallVariantGasCallEIP2929(oldCalculator gasFunc) gasFunc {
 		// outside of this function, as part of the dynamic gas, and that will make it
 		// also become correctly reported to tracers.
 		contract.Gas += coldCost
-		return gas + coldCost, nil
+
+		var overflow bool
+		if gas, overflow = math.SafeAdd(gas, coldCost); overflow {
+			return 0, ErrGasUintOverflow
+		}
+		return gas, nil
 	}
 }
 
```

### internal/ethapi/api_test.go
```diff
@@ -1796,6 +1796,7 @@ func setupReceiptBackend(t *testing.T, genBlocks int) (*testBackend, []common.Ha
 			tx  *types.Transaction
 			err error
 		)
+		b.SetPoS()
 		switch i {
 		case 0:
 			// transfer 1000wei
@@ -1844,7 +1845,6 @@ func setupReceiptBackend(t *testing.T, genBlocks int) (*testBackend, []common.Ha
 			b.AddTx(tx)
 			txHashes[i] = tx.Hash()
 		}
-		b.SetPoS()
 	})
 	return backend, txHashes
 }
```

### params/config.go
```diff
@@ -1042,6 +1042,8 @@ func (c *ChainConfig) Rules(num *big.Int, isMerge bool, timestamp uint64) Rules
 	if chainID == nil {
 		chainID = new(big.Int)
 	}
+	// disallow setting Merge out of order
+	isMerge = isMerge && c.IsLondon(num)
 	return Rules{
 		ChainID:          new(big.Int).Set(chainID),
 		IsHomestead:      c.IsHomestead(num),
@@ -1055,13 +1057,13 @@ func (c *ChainConfig) Rules(num *big.Int, isMerge bool, timestamp uint64) Rules
 		IsBerlin:         c.IsBerlin(num),
 		IsLondon:         c.IsLondon(num),
 		IsMerge:          isMerge,
-		IsShanghai:       c.IsShanghai(num, timestamp),
-		IsCancun:         c.IsCancun(num, timestamp),
-		IsPrague:         c.IsPrague(num, timestamp),
-		IsVerkle:         c.IsVerkle(num, timestamp),
+		IsShanghai:       isMerge && c.IsShanghai(num, timestamp),
+		IsCancun:         isMerge && c.IsCancun(num, timestamp),
+		IsPrague:         isMerge && c.IsPrague(num, timestamp),
+		IsVerkle:         isMerge && c.IsVerkle(num, timestamp),
 		// Optimism
-		IsOptimismBedrock:  c.IsOptimismBedrock(num),
-		IsOptimismRegolith: c.IsOptimismRegolith(timestamp),
-		IsOptimismCanyon:   c.IsOptimismCanyon(timestamp),
+		IsOptimismBedrock:  isMerge && c.IsOptimismBedrock(num),
+		IsOptimismRegolith: isMerge && c.IsOptimismRegolith(timestamp),
+		IsOptimismCanyon:   isMerge && c.IsOptimismCanyon(timestamp),
 	}
 }
```

### params/config_test.go
```diff
@@ -140,6 +140,7 @@ func TestConfigRules(t *testing.T) {
 
 func TestConfigRulesRegolith(t *testing.T) {
 	c := &ChainConfig{
+		LondonBlock:  new(big.Int),
 		RegolithTime: newUint64(500),
 		Optimism:     &OptimismConfig{},
 	}
```
