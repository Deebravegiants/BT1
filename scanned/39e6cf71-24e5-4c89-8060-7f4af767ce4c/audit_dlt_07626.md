# [?] core/vm: evm fix panic (#23047)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2021-06-16
Source: https://github.com/ethereum/go-ethereum/commit/080b6ebe9138b19d0757c57d1f537eea9b20a782
Type: security-commit

## Details
core/vm: evm fix panic (#23047)

* core/vm: evm fix panic

* core/vm/runtime: default to params.initialbasefee

## Patch
### core/vm/runtime/env.go
```diff
@@ -35,6 +35,7 @@ func NewEnv(cfg *Config) *vm.EVM {
 		Time:        cfg.Time,
 		Difficulty:  cfg.Difficulty,
 		GasLimit:    cfg.GasLimit,
+		BaseFee:     cfg.BaseFee,
 	}
 
 	return vm.NewEVM(blockContext, txContext, cfg.State, cfg.ChainConfig, cfg.EVMConfig)
```

### core/vm/runtime/runtime.go
```diff
@@ -43,6 +43,7 @@ type Config struct {
 	Value       *big.Int
 	Debug       bool
 	EVMConfig   vm.Config
+	BaseFee     *big.Int
 
 	State     *state.StateDB
 	GetHashFn func(n uint64) common.Hash
@@ -66,7 +67,7 @@ func setDefaults(cfg *Config) {
 			IstanbulBlock:       new(big.Int),
 			MuirGlacierBlock:    new(big.Int),
 			BerlinBlock:         new(big.Int),
-			LondonBlock:         nil,
+			LondonBlock:         new(big.Int),
 		}
 	}
 
@@ -93,6 +94,9 @@ func setDefaults(cfg *Config) {
 			return common.BytesToHash(crypto.Keccak256([]byte(new(big.Int).SetUint64(n).String())))
 		}
 	}
+	if cfg.BaseFee == nil {
+		cfg.BaseFee = big.NewInt(params.InitialBaseFee)
+	}
 }
 
 // Execute executes the code using the input as call data during the execution.
```
