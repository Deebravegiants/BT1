# [?] core/vm, params: ensure order of forks, prevent overflow (#29023)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2024-02-19
Source: https://github.com/ethereum/go-ethereum/commit/ac0ff044606a663eeb47ef60ed5506f842753084
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
@@ -1818,6 +1818,7 @@ func setupReceiptBackend(t *testing.T, genBlocks int) (*testBackend, []common.Ha
 			tx  *types.Transaction
 			err error
 		)
+		b.SetPoS()
 		switch i {
 		case 0:
 			// transfer 1000wei
@@ -1866,7 +1867,6 @@ func setupReceiptBackend(t *testing.T, genBlocks int) (*testBackend, []common.Ha
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
@@ -910,6 +910,8 @@ func (c *ChainConfig) Rules(num *big.Int, isMerge bool, timestamp uint64) Rules
 	if chainID == nil {
 		chainID = new(big.Int)
 	}
+	// disallow setting Merge out of order
+	isMerge = isMerge && c.IsLondon(num)
 	return Rules{
 		ChainID:          new(big.Int).Set(chainID),
 		IsHomestead:      c.IsHomestead(num),
@@ -923,9 +925,9 @@ func (c *ChainConfig) Rules(num *big.Int, isMerge bool, timestamp uint64) Rules
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
 	}
 }
```
