# [?] Avoid overflow when adding postingGas

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/go-ethereum
Published: 2025-05-20
Source: https://github.com/OffchainLabs/go-ethereum/commit/c0bc96bfef14209be6b8a046b7a7826ea0b03d9d
Type: security-commit

## Details
Avoid overflow when adding postingGas

## Patch
### internal/ethapi/transaction_args.go
```diff
@@ -23,6 +23,7 @@ import (
 	"errors"
 	"fmt"
 	"math"
+	gomath "math"
 	"math/big"
 
 	"github.com/ethereum/go-ethereum/common"
@@ -489,7 +490,11 @@ func (args *TransactionArgs) ToMessage(baseFee *big.Int, globalGasCap uint64, he
 			postingGas, err = core.RPCPostingGasHook(msg, header, state)
 		}
 		if err == nil {
-			args.setGasUsingCap(globalGasCap + postingGas)
+			if globalGasCap < gomath.MaxUint64-postingGas {
+				args.setGasUsingCap(globalGasCap + postingGas)
+			} else {
+				args.setGasUsingCap(globalGasCap)
+			}
 			msg.GasLimit = uint64(*args.Gas)
 		} else {
 			log.Error("error reading posting gas", "err", err)
```
