# [?] Prevent race condition in pointer cache (#2223)

## Summary
Severity: Unknown
Chain: Sei
Component: sei-protocol/sei-chain
Published: 2025-07-08
Source: https://github.com/sei-protocol/sei-chain/commit/9d1f37941c997bd574cd0b5e1ed3557eb177c2a5
Type: security-commit

## Details
Prevent race condition in pointer cache (#2223)

Co-authored-by: Yiming Zang <50607998+yzang2019@users.noreply.github.com>

## Patch
### utils/slice.go
```diff
@@ -38,3 +38,9 @@ func Filter[T any](slice []T, lambda func(t T) bool) []T {
 	}
 	return res
 }
+
+func Copy[T any](slice []T) []T {
+	cpy := make([]T, len(slice))
+	copy(cpy, slice)
+	return cpy
+}
```

### x/evm/artifacts/cw1155/artifacts.go
```diff
@@ -6,8 +6,10 @@ import (
 	"encoding/hex"
 	"fmt"
 	"strings"
+	"sync"
 
 	"github.com/ethereum/go-ethereum/accounts/abi"
+	"github.com/sei-protocol/sei-chain/utils"
 )
 
 const CurrentVersion uint16 = 2
@@ -18,6 +20,7 @@ var f embed.FS
 
 var cachedBin []byte
 var cachedABI *abi.ABI
+var cacheMtx *sync.RWMutex = &sync.RWMutex{}
 
 func GetABI() []byte {
 	bz, err := f.ReadFile("CW1155ERC1155Pointer.abi")
@@ -28,20 +31,20 @@ func GetABI() []byte {
 }
 
 func GetParsedABI() *abi.ABI {
-	if cachedABI != nil {
-		return cachedABI
+	if cached := getCachedABI(); cached != nil {
+		return cached
 	}
 	parsedABI, err := abi.JSON(strings.NewReader(string(GetABI())))
 	if err != nil {
 		panic(err)
 	}
-	cachedABI = &parsedABI
-	return cachedABI
+	setCachedABI(&parsedABI)
+	return &parsedABI
 }
 
 func GetBin() []byte {
-	if cachedBin != nil {
-		return cachedBin
+	if cached := getCachedBin(); len(cached) > 0 {
+		return cached
 	}
 	code, err := f.ReadFile("CW1155ERC1155Pointer.bin")
 	if err != nil {
@@ -51,8 +54,32 @@ func GetBin() []byte {
 	if err != nil {
 		panic("failed to decode CW1155ERC1155Pointer contract binary")
 	}
-	cachedBin = bz
-	return bz
+	setCachedBin(bz)
+	return utils.Copy(bz)
+}
+
+func getCachedABI() *abi.ABI {
+	cacheMtx.RLock()
+	defer cacheMtx.RUnlock()
+	return cachedABI
+}
+
+func setCachedABI(a *abi.ABI) {
+	cacheMtx.Lock()
+	defer cacheMtx.Unlock()
+	cachedABI = a
+}
+
+func getCachedBin() []byte {
+	cacheMtx.RLock()
+	defer cacheMtx.RUnlock()
+	return utils.Copy(cachedBin)
+}
+
+func setCachedBin(bin []byte) {
+	cacheMtx.Lock()
+	defer cacheMtx.Unlock()
+	cachedBin = bin
 }
 
 func IsCodeFromBin(code []byte) bool {
```

### x/evm/artifacts/cw1155/artifacts_test.go
```diff
@@ -0,0 +1,24 @@
+package cw1155_test
+
+import (
+	"sync"
+	"testing"
+
+	"github.com/sei-protocol/sei-chain/x/evm/artifacts/cw1155"
+	"github.com/stretchr/testify/require"
+)
+
+// run with `-race`
+func TestGetBinConcurrent(t *testing.T) {
+	var wg sync.WaitGroup
+
+	for i := 0; i < 100; i++ {
+		wg.Add(1)
+		go func(val int) {
+			defer wg.Done()
+			require.NotEmpty(t, cw1155.GetBin())
+		}(i)
+	}
+
+	wg.Wait()
+}
```

### x/evm/artifacts/cw20/artifacts.go
```diff
@@ -6,10 +6,12 @@ import (
 	"encoding/hex"
 	"fmt"
 	"strings"
+	"sync"
 
 	sdk "github.com/cosmos/cosmos-sdk/types"
 	"github.com/ethereum/go-ethereum/accounts/abi"
 
+	"github.com/sei-protocol/sei-chain/utils"
 	"github.com/sei-protocol/sei-chain/x/evm/config"
 )
 
@@ -35,6 +37,7 @@ var f embed.FS
 var cachedBin []byte
 var cachedLegacyBin []byte
 var cachedABI *abi.ABI
+var cacheMtx *sync.RWMutex = &sync.RWMutex{}
 
 func GetABI() []byte {
 	bz, err := f.ReadFile("CW20ERC20Pointer.abi")
@@ -45,20 +48,20 @@ func GetABI() []byte {
 }
 
 func GetParsedABI() *abi.ABI {
-	if cachedABI != nil {
-		return cachedABI
+	if cached := getCachedABI(); cached != nil {
+		return cached
 	}
 	parsedABI, err := abi.JSON(strings.NewReader(string(GetABI())))
 	if err != nil {
 		panic(err)
 	}
-	cachedABI = &parsedABI
-	return cachedABI
+	setCachedABI(&parsedABI)
+	return &parsedABI
 }
 
 func GetBin() []byte {
-	if cachedBin != nil {
-		return cachedBin
+	if cached := getCachedBin(); len(cached) > 0 {
+		return cached
 	}
 	code, err := f.ReadFile("CW20ERC20Pointer.bin")
 	if err != nil {
@@ -68,13 +71,13 @@ func GetBin() []byte {
 	if err != nil {
 		panic("failed to decode CW20ERC20 contract binary")
 	}
-	cachedBin = bz
-	return bz
+	setCachedBin(bz)
+	return utils.Copy(bz)
 }
 
 func GetLegacyBin() []byte {
-	if cachedLegacyBin != nil {
-		return cachedLegacyBin
+	if cached := getCachedLegacyBin(); len(cached) > 0 {
+		return cached
 	}
 	code, err := f.ReadFile("legacy.bin")
 	if err != nil {
@@ -84,8 +87,44 @@ func GetLegacyBin() []byte {
 	if err != nil {
 		panic("failed to decode CW20ERC20 legacy contract binary")
 	}
-	cachedLegacyBin = bz
-	return bz
+	setCachedLegacyBin(bz)
+	return utils.Copy(bz)
+}
+
+func getCachedABI() *abi.ABI {
+	cacheMtx.RLock()
+	defer cacheMtx.RUnlock()
+	return cachedABI
+}
+
+func setCachedABI(a *abi.ABI) {
+	cacheMtx.Lock()
+	defer cacheMtx.Unlock()
+	cachedABI = a
+}
+
+func getCachedBin() []byte {
+	cacheMtx.RLock()
+	defer cacheMtx.RUnlock()
+	return utils.Copy(cachedBin)
+}
+
+func setCachedBin(bin []byte) {
+	cacheMtx.Lock()
+	defer cacheMtx.Unlock()
+	cachedBin = bin
+}
+
+func getCachedLegacyBin() []byte {
+	cacheMtx.RLock()
+	defer cacheMtx.RUnlock()
+	return utils.Copy(cachedLegacyBin)
+}
+
+func setCachedLegacyBin(bin []byte) {
+	cacheMtx.Lock()
+	defer cacheMtx.Unlock()
+	cachedLegacyBin = bin
 }
 
 func IsCodeFromBin(code []byte) bool {
```

### x/evm/artifacts/cw20/artifacts_test.go
```diff
@@ -0,0 +1,24 @@
+package cw20_test
+
+import (
+	"sync"
+	"testing"
+
+	"github.com/sei-protocol/sei-chain/x/evm/artifacts/cw20"
+	"github.com/stretchr/testify/require"
+)
+
+// run with `-race`
+func TestGetBinConcurrent(t *testing.T) {
+	var wg sync.WaitGroup
+
+	for i := 0; i < 100; i++ {
+		wg.Add(1)
+		go func(val int) {
+			defer wg.Done()
+			require.NotEmpty(t, cw20.GetBin())
+		}(i)
+	}
+
+	wg.Wait()
+}
```

### x/evm/artifacts/cw721/artifacts.go
```diff
@@ -6,8 +6,10 @@ import (
 	"encoding/hex"
 	"fmt"
 	"strings"
+	"sync"
 
 	"github.com/ethereum/go-ethereum/accounts/abi"
+	"github.com/sei-protocol/sei-chain/utils"
 )
 
 const CurrentVersion uint16 = 6
@@ -20,6 +22,7 @@ var f embed.FS
 var cachedBin []byte
 var cachedLegacyBin []byte
 var cachedABI *abi.ABI
+var cacheMtx *sync.RWMutex = &sync.RWMutex{}
 
 func GetABI() []byte {
 	bz, err := f.ReadFile("CW721ERC721Pointer.abi")
@@ -30,20 +33,20 @@ func GetABI() []byte {
 }
 
 func GetParsedABI() *abi.ABI {
-	if cachedABI != nil {
-		return cachedABI
+	if cached := getCachedABI(); cached != nil {
+		return cached
 	}
 	parsedABI, err := abi.JSON(strings.NewReader(string(GetABI())))
 	if err != nil {
 		panic(err)
 	}
-	cachedABI = &parsedABI
-	return cachedABI
+	setCachedABI(&parsedABI)
+	return &parsedABI
 }
 
 func GetBin() []byte {
-	if cachedBin != nil {
-		return cachedBin
+	if cached := getCachedBin(); len(cached) > 0 {
+		return cached
 	}
 	code, err := f.ReadFile("CW721ERC721Pointer.bin")
 	if err != nil {
@@ -53,13 +56,13 @@ func GetBin() []byte {
 	if err != nil {
 		panic("failed to decode CW721ERC721Pointer contract binary")
 	}
-	cachedBin = bz
-	return bz
+	setCachedBin(bz)
+	return utils.Copy(bz)
 }
 
 func GetLegacyBin() []byte {
-	if cachedLegacyBin != nil {
-		return cachedLegacyBin
+	if cached := getCachedLegacyBin(); len(cached) > 0 {
+		return cached
 	}
 	code, err := f.ReadFile("legacy.bin")
 	if err != nil {
@@ -69,8 +72,44 @@ func GetLegacyBin() []byte {
 	if err != nil {
 		panic("failed to decode CW721ERC721Pointer legacy contract binary")
 	}
-	cachedLegacyBin = bz
-	return bz
+	setCachedLegacyBin(bz)
+	return utils.Copy(bz)
+}
+
+func getCachedABI() *abi.ABI {
+	cacheMtx.RLock()
+	defer cacheMtx.RUnlock()
+	return cachedABI
+}
+
+func setCachedABI(a *abi.ABI) {
+	cacheMtx.Lock()
+	defer cacheMtx.Unlock()
+	cachedABI = a
+}
+
+func getCachedBin() []byte {
+	cacheMtx.RLock()
+	defer cacheMtx.RUnlock()
+	return utils.Copy(cachedBin)
+}
+
+func setCachedBin(bin []byte) {
+	cacheMtx.Lock()
+	defer cacheMtx.Unlock()
+	cachedBin = bin
+}
+
+func getCachedLegacyBin() []byte {
+	cacheMtx.RLock()
+	defer cacheMtx.RUnlock()
+	return utils.Copy(cachedLegacyBin)
+}
+
+func setCachedLegacyBin(bin []byte) {
+	cacheMtx.Lock()
+	defer cacheMtx.Unlock()
+	cachedLegacyBin = bin
 }
 
 func IsCodeFromBin(code []byte) bool {
```

### x/evm/artifacts/cw721/artifacts_test.go
```diff
@@ -0,0 +1,24 @@
+package cw721_test
+
+import (
+	"sync"
+	"testing"
+
+	"github.com/sei-protocol/sei-chain/x/evm/artifacts/cw721"
+	"github.com/stretchr/testify/require"
+)
+
+// run with `-race`
+func TestGetBinConcurrent(t *testing.T) {
+	var wg sync.WaitGroup
+
+	for i := 0; i < 100; i++ {
+		wg.Add(1)
+		go func(val int) {
+			defer wg.Done()
+			require.NotEmpty(t, cw721.GetBin())
+		}(i)
+	}
+
+	wg.Wait()
+}
```

### x/evm/artifacts/erc1155/artifacts.go
```diff
@@ -1,22 +1,40 @@
 package erc1155
 
-import "embed"
+import (
+	"embed"
+	"sync"
+
+	"github.com/sei-protocol/sei-chain/utils"
+)
 
 const CurrentVersion uint16 = 1
 
 //go:embed cwerc1155.wasm
 var f embed.FS
 
 var cachedBin []byte
+var cacheMtx = &sync.RWMutex{}
 
 func GetBin() []byte {
-	if cachedBin != nil {
-		return cachedBin
+	if cached := getCachedBin(); len(cached) > 0 {
+		return cached
 	}
 	bz, err := f.ReadFile("cwerc1155.wasm")
 	if err != nil {
 		panic("failed to read ERC1155 wrapper contract wasm")
 	}
-	cachedBin = bz
-	return bz
+	setCachedBin(bz)
+	return utils.Copy(bz)
+}
+
+func getCachedBin() []byte {
+	cacheMtx.RLock()
+	defer cacheMtx.RUnlock()
+	return utils.Copy(cachedBin)
+}
+
+func setCachedBin(bin []byte) {
+	cacheMtx.Lock()
+	defer cacheMtx.Unlock()
+	cachedBin = bin
 }
```

### x/evm/artifacts/erc1155/artifacts_test.go
```diff
@@ -0,0 +1,24 @@
+package erc1155_test
+
+import (
+	"sync"
+	"testing"
+
+	"github.com/sei-protocol/sei-chain/x/evm/artifacts/erc1155"
+	"github.com/stretchr/testify/require"
+)
+
+// run with `-race`
+func TestGetBinConcurrent(t *testing.T) {
+	var wg sync.WaitGroup
+
+	for i := 0; i < 100; i++ {
+		wg.Add(1)
+		go func(val int) {
+			defer wg.Done()
+			require.NotEmpty(t, erc1155.GetBin())
+		}(i)
+	}
+
+	wg.Wait()
+}
```

### x/evm/artifacts/erc20/artifacts.go
```diff
@@ -1,22 +1,40 @@
 package erc20
 
-import "embed"
+import (
+	"embed"
+	"sync"
+
+	"github.com/sei-protocol/sei-chain/utils"
+)
 
 const CurrentVersion uint16 = 2
 
 //go:embed cwerc20.wasm
 var f embed.FS
 
 var cachedBin []byte
+var cacheMtx *sync.RWMutex = &sync.RWMutex{}
 
 func GetBin() []byte {
-	if cachedBin != nil {
-		return cachedBin
+	if cached := getCachedBin(); len(cached) > 0 {
+		return cached
 	}
 	bz, err := f.ReadFile("cwerc20.wasm")
 	if err != nil {
 		panic("failed to read ERC20 wrapper contract wasm")
 	}
-	cachedBin = bz
-	return bz
+	setCachedBin(bz)
+	return utils.Copy(bz)
+}
+
+func getCachedBin() []byte {
+	cacheMtx.RLock()
+	defer cacheMtx.RUnlock()
+	return utils.Copy(cachedBin)
+}
+
+func setCachedBin(bin []byte) {
+	cacheMtx.Lock()
+	defer cacheMtx.Unlock()
+	cachedBin = bin
 }
```

### x/evm/artifacts/erc20/artifacts_test.go
```diff
@@ -0,0 +1,24 @@
+package erc20_test
+
+import (
+	"sync"
+	"testing"
+
+	"github.com/sei-protocol/sei-chain/x/evm/artifacts/erc20"
+	"github.com/stretchr/testify/require"
+)
+
+// run with `-race`
+func TestGetBinConcurrent(t *testing.T) {
+	var wg sync.WaitGroup
+
+	for i := 0; i < 100; i++ {
+		wg.Add(1)
+		go func(val int) {
+			defer wg.Done()
+			require.NotEmpty(t, erc20.GetBin())
+		}(i)
+	}
+
+	wg.Wait()
+}
```

### x/evm/artifacts/erc721/artifacts.go
```diff
@@ -1,22 +1,40 @@
 package erc721
 
-import "embed"
+import (
+	"embed"
+	"sync"
+
+	"github.com/sei-protocol/sei-chain/utils"
+)
 
 const CurrentVersion uint16 = 6
 
 //go:embed cwerc721.wasm
 var f embed.FS
 
 var cachedBin []byte
+var cacheMtx *sync.RWMutex = &sync.RWMutex{}
 
 func GetBin() []byte {
-	if cachedBin != nil {
-		return cachedBin
+	if cached := getCachedBin(); len(cached) > 0 {
+		return cached
 	}
 	bz, err := f.ReadFile("cwerc721.wasm")
 	if err != nil {
 		panic("failed to read ERC721 wrapper contract wasm")
 	}
-	cachedBin = bz
-	return bz
+	setCachedBin(bz)
+	return utils.Copy(bz)
+}
+
+func getCachedBin() []byte {
+	cacheMtx.RLock()
+	defer cacheMtx.RUnlock()
+	return utils.Copy(cachedBin)
+}
+
+func setCachedBin(bin []byte) {
+	cacheMtx.Lock()
+	defer cacheMtx.Unlock()
+	cachedBin = bin
 }
```
