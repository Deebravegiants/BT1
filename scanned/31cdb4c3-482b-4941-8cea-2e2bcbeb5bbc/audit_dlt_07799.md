# [?] Fix FuzzForkChoiceResponse Crash (#11043)

## Summary
Severity: Unknown
Chain: Ethereum
Component: OffchainLabs/prysm
Published: 2022-07-13
Source: https://github.com/OffchainLabs/prysm/commit/b0e15f3c8fca06476bdf57b9fcf81d9f83840745
Type: security-commit

## Details
Fix FuzzForkChoiceResponse Crash (#11043)

## Patch
### beacon-chain/powchain/testdata/fuzz/FuzzForkChoiceResponse/2d0486b744e252db538db5a44bfd6e6e22ff2723
```diff
@@ -0,0 +1,2 @@
+go test fuzz v1
+[]byte("{\"0000000000000\":{},\"pAYloAdId\":\"\"}")
\ No newline at end of file
```

### proto/engine/v1/json_marshal_unmarshal.go
```diff
@@ -3,6 +3,7 @@ package enginev1
 import (
 	"encoding/json"
 	"math/big"
+	"reflect"
 	"strings"
 
 	"github.com/ethereum/go-ethereum/common"
@@ -96,12 +97,10 @@ func (e *ExecutionBlock) UnmarshalJSON(enc []byte) error {
 
 // UnmarshalJSON --
 func (b *PayloadIDBytes) UnmarshalJSON(enc []byte) error {
-	hexBytes := hexutil.Bytes(make([]byte, 0))
-	if err := json.Unmarshal(enc, &hexBytes); err != nil {
+	res := [8]byte{}
+	if err := hexutil.UnmarshalFixedJSON(reflect.TypeOf(b), enc, res[:]); err != nil {
 		return err
 	}
-	res := [8]byte{}
-	copy(res[:], hexBytes)
 	*b = res
 	return nil
 }
```
