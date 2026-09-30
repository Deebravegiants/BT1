# [?] params/types/genesisT: fix stack overflows during state processor tests

## Summary
Severity: Unknown
Chain: Ethereum Classic
Component: etclabscore/core-geth
Published: 2022-06-20
Source: https://github.com/etclabscore/core-geth/commit/a4095bbeff351da4f5870ecc881685ef6e2a0403
Type: security-commit

## Details
params/types/genesisT: fix stack overflows during state processor tests

Date: 2022-06-20 12:55:45-07:00
Signed-off-by: meows <b5c6@protonmail.com>

## Patch
### params/types/genesisT/genesis.go
```diff
@@ -25,7 +25,6 @@ import (
 	"math/big"
 	"strings"
 
-	"github.com/davecgh/go-spew/spew"
 	"github.com/ethereum/go-ethereum/common"
 	"github.com/ethereum/go-ethereum/common/hexutil"
 	"github.com/ethereum/go-ethereum/common/math"
@@ -877,5 +876,6 @@ func (g *Genesis) SetLyra2NonceTransition(n *uint64) error {
 }
 
 func (g *Genesis) String() string {
-	return spew.Sdump(g)
+	j, _ := json.MarshalIndent(g, "", "    ")
+	return "Genesis: " + string(j)
 }
```
