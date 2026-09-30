# [?] params/types/multigeth: fix multigeth String method to not stack overflow

## Summary
Severity: Unknown
Chain: Ethereum Classic
Component: etclabscore/core-geth
Published: 2022-06-21
Source: https://github.com/etclabscore/core-geth/commit/74c4798f7de3e1443e559f0f532bea8bbdbc1ede
Type: security-commit

## Details
params/types/multigeth: fix multigeth String method to not stack overflow

Date: 2022-06-21 12:11:12-07:00
Signed-off-by: meows <b5c6@protonmail.com>

## Patch
### params/types/multigeth/multigethv0_chain_config_configurator.go
```diff
@@ -1,9 +1,9 @@
 package multigeth
 
 import (
+	"encoding/json"
 	"math/big"
 
-	"github.com/davecgh/go-spew/spew"
 	"github.com/ethereum/go-ethereum/common"
 	"github.com/ethereum/go-ethereum/params/types/ctypes"
 	"github.com/ethereum/go-ethereum/params/types/internal"
@@ -1036,5 +1036,6 @@ func (c *ChainConfig) SetLyra2NonceTransition(n *uint64) error {
 }
 
 func (c *ChainConfig) String() string {
-	return spew.Sdump(c)
+	j, _ := json.MarshalIndent(c, "", "    ")
+	return "Multigeth Config: " + string(j)
 }
```
