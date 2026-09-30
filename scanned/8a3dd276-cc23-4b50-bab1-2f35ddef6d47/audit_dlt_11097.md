# [?] genesis: fix permit2 panic (#10332)

## Summary
Severity: Unknown
Chain: Boba
Component: bobanetwork/boba
Published: 2024-04-30
Source: https://github.com/bobanetwork/boba/commit/acd8cf8aa16d0e59508ee402458a97945f03e1c6
Type: security-commit

## Details
genesis: fix permit2 panic (#10332)

* genesis: fix permit2 panic

Its possible that permit2 isn't in the genesis allocs even
though it should be, it removes the flexibility to define the
genesis spec arbitrarily if we implicitly enforce it being present.
We need a better way to check that the chain id during genesis
allocation matches the chain id in the genesis spec.
An attempt at this is done in https://github.com/ethereum-optimism/optimism/pull/10326.

Fixes https://github.com/ethereum-optimism/optimism/issues/10309

* op-chain-ops: better check

* cleanup: fix build

* build: fix

## Patch
### op-chain-ops/genesis/helpers.go
```diff
@@ -1,7 +1,6 @@
 package genesis
 
 import (
-	"bytes"
 	"context"
 	"fmt"
 	"math/big"
@@ -14,18 +13,12 @@ import (
 )
 
 var (
-	// codeNamespace represents the namespace of implementations of predeploys
-	codeNamespace = common.HexToAddress("0xc0D3C0d3C0d3C0D3c0d3C0d3c0D3C0d3c0d30000")
-	// l2PredeployNamespace represents the namespace of L2 predeploys
-	l2PredeployNamespace = common.HexToAddress("0x4200000000000000000000000000000000000000")
-	// BigL2PredeployNamespace represents the predeploy namespace as a big.Int
-	BigL2PredeployNamespace = new(big.Int).SetBytes(l2PredeployNamespace.Bytes())
-	// bigCodeNamespace represents the predeploy namespace as a big.Int
-	bigCodeNamespace = new(big.Int).SetBytes(codeNamespace.Bytes())
 	// ImplementationSlot represents the EIP 1967 implementation storage slot
 	ImplementationSlot = common.HexToHash("0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc")
 	// AdminSlot represents the EIP 1967 admin storage slot
 	AdminSlot = common.HexToHash("0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103")
+	// The devBalance is the amount of wei that a dev account is funded with.
+	devBalance = hexutil.MustDecodeBig("0x200000000000000000000000000000000000000000000000000000000000000")
 )
 
 // DevAccounts represent the standard hardhat development accounts.
@@ -59,24 +52,6 @@ var DevAccounts = []common.Address{
 	common.HexToAddress("0x3fab184622dc19b6109349b94811493bf2a45362"),
 }
 
-// The devBalance is the amount of wei that a dev account is funded with.
-var devBalance = hexutil.MustDecodeBig("0x200000000000000000000000000000000000000000000000000000000000000")
-
-// AddressToCodeNamespace takes a predeploy address and computes
-// the implementation address that the implementation should be deployed at
-func AddressToCodeNamespace(addr common.Address) (common.Address, error) {
-	if !IsL2DevPredeploy(addr) {
-		return common.Address{}, fmt.Errorf("cannot handle non predeploy: %s", addr)
-	}
-	bigAddress := new(big.Int).SetBytes(addr[18:])
-	num := new(big.Int).Or(bigCodeNamespace, bigAddress)
-	return common.BigToAddress(num), nil
-}
-
-func IsL2DevPredeploy(addr common.Address) bool {
-	return bytes.Equal(addr[0:2], []byte{0x42, 0x00})
-}
-
 // GetBlockFromTag will resolve a Block given an rpc block tag
 func GetBlockFromTag(chain ethereum.ChainReader, tag *rpc.BlockNumberOrHash) (*types.Block, error) {
 	if hash, ok := tag.Hash(); ok {
```

### op-chain-ops/genesis/layer_two.go
```diff
@@ -3,13 +3,15 @@ package genesis
 import (
 	"encoding/json"
 	"fmt"
+	"math/big"
 	"os"
 	"path/filepath"
 
 	hdwallet "github.com/ethereum-optimism/go-ethereum-hdwallet"
 	"github.com/holiman/uint256"
 
 	"github.com/ethereum/go-ethereum/accounts"
+	"github.com/ethereum/go-ethereum/common"
 	"github.com/ethereum/go-ethereum/core"
 	"github.com/ethereum/go-ethereum/core/types"
 	"github.com/ethereum/go-ethereum/crypto"
@@ -24,6 +26,13 @@ const (
 	L2AllocsEcotone L2AllocsMode = "" // the default in solidity scripting / testing
 )
 
+var (
+	// l2PredeployNamespace is the namespace for L2 predeploys
+	l2PredeployNamespace = common.HexToAddress("0x4200000000000000000000000000000000000000")
+	// mnemonic for the test accounts in hardhat/foundry
+	testMnemonic = "test test test test test test test test test test test junk"
+)
+
 type AllocsLoader func(mode L2AllocsMode) *ForgeAllocs
 
 // BuildL2Genesis will build the L2 genesis block.
@@ -40,16 +49,27 @@ func BuildL2Genesis(config *DeployConfig, dump *ForgeAllocs, l1StartBlock *types
 		return nil, fmt.Errorf("deploy config mismatch with allocs. Deploy config fundDevAccounts: %v, actual allocs: %v", config.FundDevAccounts, hasDevAccounts)
 	}
 	// sanity check the permit2 immutable, to verify we using the allocs for the right chain.
-	chainID := [32]byte(genspec.Alloc[predeploys.Permit2Addr].Code[6945 : 6945+32])
-	expected := uint256.MustFromBig(genspec.Config.ChainID).Bytes32()
-	if chainID != expected {
-		return nil, fmt.Errorf("allocs were generated for chain ID %x, but expected chain %x (%d)", chainID, expected, genspec.Config.ChainID)
+	if permit2 := genspec.Alloc[predeploys.Permit2Addr].Code; len(permit2) != 0 {
+		if len(permit2) < 6945+32 {
+			return nil, fmt.Errorf("permit2 code is too short (%d)", len(permit2))
+		}
+		chainID := [32]byte(permit2[6945 : 6945+32])
+		expected := uint256.MustFromBig(genspec.Config.ChainID).Bytes32()
+		if chainID != expected {
+			return nil, fmt.Errorf("allocs were generated for chain ID %x, but expected chain %x (%d)", chainID, expected, genspec.Config.ChainID)
+		}
 	}
+	// sanity check that all predeploys are present
+	for i := 0; i < 2048; i++ {
+		addr := common.BigToAddress(new(big.Int).Or(l2PredeployNamespace.Big(), big.NewInt(int64(i))))
+		if len(genspec.Alloc[addr].Code) == 0 {
+			return nil, fmt.Errorf("predeploy %x is missing from L2 genesis allocs", addr)
+		}
+	}
+
 	return genspec, nil
 }
 
-var testMnemonic = "test test test test test test test test test test test junk"
-
 func HasAnyDevAccounts(allocs core.GenesisAlloc) (bool, error) {
 	wallet, err := hdwallet.NewFromMnemonic(testMnemonic)
 	if err != nil {
```
