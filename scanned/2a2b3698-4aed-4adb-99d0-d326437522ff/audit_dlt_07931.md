# [?] vm: add two proof verifier to fix the vulnerability in range proof (#1121)

## Summary
Severity: Unknown
Chain: BNB Chain
Component: bnb-chain/bsc
Published: 2022-10-11
Source: https://github.com/bnb-chain/bsc/commit/cb131fabe5fb9570180e7030a293a984f17c2446
Type: security-commit

## Details
vm: add two proof verifier to fix the vulnerability in range proof (#1121)

## Patch
### CHANGELOG.md
```diff
@@ -1,5 +1,8 @@
 # Changelog
 
+## v1.1.16
+* [\#1121](https://github.com/bnb-chain/bsc/pull/1121) vm: add two proof verifier to fix the vulnerability in range proof
+
 ## v1.1.15
 * [\#1109](https://github.com/bnb-chain/bsc/pull/1109) nanofork: block exploitation accounts and suspend cross chain bridge related precompile contracts
 
```

### accounts/abi/bind/bind_test.go
```diff
@@ -2023,6 +2023,12 @@ func TestGolangBindings(t *testing.T) {
 	if out, err := replacer.CombinedOutput(); err != nil {
 		t.Fatalf("failed to replace binding test dependency to current source tree: %v\n%s", err, out)
 	}
+
+	replacer = exec.Command(gocmd, "mod", "edit", "-x", "-require", "github.com/tendermint/tendermint@v0.0.0", "-replace", "github.com/tendermint/tendermint=github.com/bnb-chain/tendermint@v0.31.12") // Repo root
+	replacer.Dir = pkg
+	if out, err := replacer.CombinedOutput(); err != nil {
+		t.Fatalf("failed to replace tendermint dependency to bnb-chain source: %v\n%s", err, out)
+	}
 	tidier := exec.Command(gocmd, "mod", "tidy")
 	tidier.Dir = pkg
 	if out, err := tidier.CombinedOutput(); err != nil {
```

### core/types/blacklist.go
```diff
@@ -2,7 +2,7 @@ package types
 
 import "github.com/ethereum/go-ethereum/common"
 
-// This is introduced because of the Tendermint IAVL Merkel Proof verification exploitation.
+// This is introduced because of the Tendermint IAVL Merkle Proof verification exploitation.
 var NanoBlackList = []common.Address{
 	common.HexToAddress("0x489A8756C18C0b8B24EC2a2b9FF3D4d447F79BEc"),
 	common.HexToAddress("0xFd6042Df3D74ce9959922FeC559d7995F3933c55"),
```

### core/vm/contracts.go
```diff
@@ -96,6 +96,21 @@ var PrecompiledContractsIsNano = map[common.Address]PrecompiledContract{
 	common.BytesToAddress([]byte{101}): &iavlMerkleProofValidateNano{},
 }
 
+var PrecompiledContractsIsMoran = map[common.Address]PrecompiledContract{
+	common.BytesToAddress([]byte{1}): &ecrecover{},
+	common.BytesToAddress([]byte{2}): &sha256hash{},
+	common.BytesToAddress([]byte{3}): &ripemd160hash{},
+	common.BytesToAddress([]byte{4}): &dataCopy{},
+	common.BytesToAddress([]byte{5}): &bigModExp{},
+	common.BytesToAddress([]byte{6}): &bn256AddIstanbul{},
+	common.BytesToAddress([]byte{7}): &bn256ScalarMulIstanbul{},
+	common.BytesToAddress([]byte{8}): &bn256PairingIstanbul{},
+	common.BytesToAddress([]byte{9}): &blake2F{},
+
+	common.BytesToAddress([]byte{100}): &tmHeaderValidate{},
+	common.BytesToAddress([]byte{101}): &iavlMerkleProofValidateMoran{},
+}
+
 // PrecompiledContractsBerlin contains the default set of pre-compiled Ethereum
 // contracts used in the Berlin release.
 var PrecompiledContractsBerlin = map[common.Address]PrecompiledContract{
@@ -125,6 +140,7 @@ var PrecompiledContractsBLS = map[common.Address]PrecompiledContract{
 }
 
 var (
+	PrecompiledAddressesMoran     []common.Address
 	PrecompiledAddressesNano      []common.Address
 	PrecompiledAddressesBerlin    []common.Address
 	PrecompiledAddressesIstanbul  []common.Address
@@ -148,11 +164,17 @@ func init() {
 	for k := range PrecompiledContractsIsNano {
 		PrecompiledAddressesNano = append(PrecompiledAddressesNano, k)
 	}
+
+	for k := range PrecompiledContractsIsMoran {
+		PrecompiledAddressesMoran = append(PrecompiledAddressesMoran, k)
+	}
 }
 
 // ActivePrecompiles returns the precompiles enabled with the current configuration.
 func ActivePrecompiles(rules params.Rules) []common.Address {
 	switch {
+	case rules.IsMoran:
+		return PrecompiledAddressesMoran
 	case rules.IsNano:
 		return PrecompiledAddressesNano
 	case rules.IsBerlin:
```

### core/vm/contracts_lightclient.go
```diff
@@ -4,6 +4,10 @@ import (
 	"encoding/binary"
 	"fmt"
 
+	"github.com/tendermint/iavl"
+	"github.com/tendermint/tendermint/crypto/merkle"
+	cmn "github.com/tendermint/tendermint/libs/common"
+
 	"github.com/ethereum/go-ethereum/core/vm/lightclient"
 	"github.com/ethereum/go-ethereum/params"
 )
@@ -93,8 +97,10 @@ func (c *tmHeaderValidate) Run(input []byte) (result []byte, err error) {
 
 //------------------------------------------------------------------------------------------------------------------------------------------------
 
-// tmHeaderValidate implemented as a native contract.
-type iavlMerkleProofValidate struct{}
+// iavlMerkleProofValidate implemented as a native contract.
+type iavlMerkleProofValidate struct {
+	basicIavlMerkleProofValidate
+}
 
 func (c *iavlMerkleProofValidate) RequiredGas(input []byte) uint64 {
 	return params.IAVLMerkleProofValidateGas
@@ -104,7 +110,54 @@ func (c *iavlMerkleProofValidate) RequiredGas(input []byte) uint64 {
 // | payload length | payload    |
 // | 32 bytes       |            |
 func (c *iavlMerkleProofValidate) Run(input []byte) (result []byte, err error) {
-	//return nil, fmt.Errorf("suspend")
+	return c.basicIavlMerkleProofValidate.Run(input)
+}
+
+// tmHeaderValidate implemented as a native contract.
+type tmHeaderValidateNano struct{}
+
+func (c *tmHeaderValidateNano) RequiredGas(input []byte) uint64 {
+	return params.TendermintHeaderValidateGas
+}
+
+func (c *tmHeaderValidateNano) Run(input []byte) (result []byte, err error) {
+	return nil, fmt.Errorf("suspend")
+}
+
+type iavlMerkleProofValidateNano struct{}
+
+func (c *iavlMerkleProofValidateNano) RequiredGas(_ []byte) uint64 {
+	return params.IAVLMerkleProofValidateGas
+}
+
+func (c *iavlMerkleProofValidateNano) Run(_ []byte) (result []byte, err error) {
+	return nil, fmt.Errorf("suspend")
+}
+
+//------------------------------------------------------------------------------------------------------------------------------------------------
+type iavlMerkleProofValidateMoran struct {
+	basicIavlMerkleProofValidate
+}
+
+func (c *iavlMerkleProofValidateMoran) RequiredGas(_ []byte) uint64 {
+	return params.IAVLMerkleProofValidateGas
+}
+
+func (c *iavlMerkleProofValidateMoran) Run(input []byte) (result []byte, err error) {
+	c.basicIavlMerkleProofValidate.verifiers = []merkle.ProofOpVerifier{
+		forbiddenAbsenceOpVerifier,
+		singleValueOpVerifier,
+		multiStoreOpVerifier,
+		forbiddenSimpleValueOpVerifier,
+	}
+	return c.basicIavlMerkleProofValidate.Run(input)
+}
+
+type basicIavlMerkleProofValidate struct {
+	verifiers []merkle.ProofOpVerifier
+}
+
+func (c *basicIavlMerkleProofValidate) Run(input []byte) (result []byte, err error) {
 	defer func() {
 		if r := recover(); r != nil {
 			err = fmt.Errorf("internal error: %v\n", r)
@@ -124,7 +177,7 @@ func (c *iavlMerkleProofValidate) Run(input []byte) (result []byte, err error) {
 	if err != nil {
 		return nil, err
 	}
-
+	kvmp.SetVerifiers(c.verifiers)
 	valid := kvmp.Validate()
 	if !valid {
 		return nil, fmt.Errorf("invalid merkle proof")
@@ -135,27 +188,56 @@ func (c *iavlMerkleProofValidate) Run(input []byte) (result []byte, err error) {
 	return result, nil
 }
 
-// tmHeaderValidate implemented as a native contract.
-type tmHeaderValidateNano struct{}
-
-func (c *tmHeaderValidateNano) RequiredGas(input []byte) uint64 {
-	return params.TendermintHeaderValidateGas
+func forbiddenAbsenceOpVerifier(op merkle.ProofOperator) error {
+	if op == nil {
+		return nil
+	}
+	if _, ok := op.(iavl.IAVLAbsenceOp); ok {
+		return cmn.NewError("absence proof suspend")
+	}
+	return nil
 }
 
-func (c *tmHeaderValidateNano) Run(input []byte) (result []byte, err error) {
-	return nil, fmt.Errorf("suspend")
+func forbiddenSimpleValueOpVerifier(op merkle.ProofOperator) error {
+	if op == nil {
+		return nil
+	}
+	if _, ok := op.(merkle.SimpleValueOp); ok {
+		return cmn.NewError("simple value proof suspend")
+	}
+	return nil
 }
 
-//------------------------------------------------------------------------------------------------------------------------------------------------
-type iavlMerkleProofValidateNano struct{}
-
-func (c *iavlMerkleProofValidateNano) RequiredGas(input []byte) uint64 {
-	return params.IAVLMerkleProofValidateGas
+func multiStoreOpVerifier(op merkle.ProofOperator) error {
+	if op == nil {
+		return nil
+	}
+	if mop, ok := op.(lightclient.MultiStoreProofOp); ok {
+		storeNames := make(map[string]bool, len(mop.Proof.StoreInfos))
+		for _, store := range mop.Proof.StoreInfos {
+			if exist := storeNames[store.Name]; exist {
+				return cmn.NewError("duplicated store")
+			} else {
+				storeNames[store.Name] = true
+			}
+		}
+	}
+	return nil
 }
 
-// input:
-// | payload length | payload    |
-// | 32 bytes       |            |
-func (c *iavlMerkleProofValidateNano) Run(input []byte) (result []byte, err error) {
-	return nil, fmt.Errorf("suspend")
+func singleValueOpVerifier(op merkle.ProofOperator) error {
+	if op == nil {
+		return nil
+	}
+	if valueOp, ok := op.(iavl.IAVLValueOp); ok {
+		if len(valueOp.Proof.Leaves) != 1 {
+			return cmn.NewError("range proof suspended")
+		}
+		for _, innerNode := range valueOp.Proof.LeftPath {
+			if len(innerNode.Right) > 0 && len(innerNode.Left) > 0 {
+				return cmn.NewError("both right and left hash exit!")
+			}
+		}
+	}
+	return nil
 }
```

### core/vm/contracts_lightclient_test.go
```diff
@@ -5,6 +5,8 @@ import (
 	"encoding/hex"
 	"testing"
 
+	"github.com/stretchr/testify/assert"
+
 	"github.com/ethereum/go-ethereum/core/vm/lightclient"
 	"github.com/stretchr/testify/require"
 )
@@ -102,4 +104,94 @@ func TestTmHeaderValidateAndMerkleProofValidate(t *testing.T) {
 	expectedResult := make([]byte, 32)
 	binary.BigEndian.PutUint64(expectedResult[24:], 0x01)
 	require.Equal(t, expectedResult, success)
+
+	moranValidateContract := iavlMerkleProofValidateMoran{}
+	success, err = moranValidateContract.Run(input)
+	require.NoError(t, err)
+	expectedResult = make([]byte, 32)
+	binary.BigEndian.PutUint64(expectedResult[24:], 0x01)
+	require.Equal(t, expectedResult, success)
+}
+
+func TestMerkleProofValidateMoran(t *testing.T) {
+	// Bytest1 is the inputs of exploit tx 0x05356fd06ce56a9ec5b4eaf9c075abd740cae4c21eab1676440ab5cd2fe5c57a
+	bytest1, _ := hex.DecodeString("00000000000000000000000000000000000000000000000000000000000005086962630000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000e00000100380200000000010dd9ac0000000000000000000000000000000000000000000000000000000000000093000000000000000000000000000000000000000000000000000000000000000000f870a0424e4200000000000000000000000000000000000000000000000000000000009400000000000000000000000000000000000000008ad3c21bcecceda100000094489a8756c18c0b8b24ec2a2b9ff3d4d447f79bec94489a8756c18c0b8b24ec2a2b9ff3d4d447f79bec846553f10072cda827a83531ca0fd7ac917a6b65649719aab0836722caafe0603147a523180a8d020a066961766c3a76120e00000100380200000000010dd9ac1af201f0010aed010a2b0802100318b091c73422200c10f902d266c238a4ca9e26fa9bc36483cd3ebee4e263012f5e7f40c22ee4d20a4d0801100218b091c7342220e4fd47bffd1c06e67edad92b2bf9ca63631978676288a2aa99f95c459436ef632a20121a1f9c4eca726c725796c5375fc4158986ced08e498dc8268ef94d8ed1891612001a370a0e0000010038020000000000000002122011056c6919f02d966991c10721684a8d1542e44003f9ffb47032c18995d4ac7f18b091c7341a340a0e00000100380200000000010dd9ac12202c3a561458f8527b002b5ec3cab2d308662798d6245d4588a4e6a80ebdfe30ac18010ad4050a0a6d756c746973746f726512036962631ac005be050abb050a110a066f7261636c6512070a0508b891c7340a0f0a046d61696e12070a0508b891c7340a350a08736c617368696e6712290a2708b891c7341220c8ccf341e6e695e7e1cb0ce4bf347eea0cc16947d8b4e934ec400b57c59d6f860a380a0b61746f6d69635f7377617012290a2708b891c734122042d4ecc9468f71a70288a95d46564bfcaf2c9f811051dcc5593dbef152976b010a110a0662726964676512070a0508b891c7340a300a0364657812290a2708b891c73412201773be443c27f61075cecdc050ce22eb4990c54679089e90afdc4e0e88182a230a2f0a02736312290a2708b891c7341220df7a0484b7244f76861b1642cfb7a61d923794bd2e076c8dbd05fc4ee29f3a670a330a06746f6b656e7312290a2708b891c734122064958c2f76fec1fa5d1828296e51264c259fa264f499724795a740f48fc4731b0a320a057374616b6512290a2708b891c734122015d2c302143bdf029d58fe381cc3b54cedf77ecb8834dfc5dc3e1555d68f19ab0a330a06706172616d7312290a2708b891c734122050abddcb7c115123a5a4247613ab39e6ba935a3d4f4b9123c4fedfa0895c040a0a300a0361636312290a2708b891c734122079fb5aecc4a9b87e56231103affa5e515a1bdf3d0366490a73e087980b7f1f260a0e0a0376616c12070a0508b891c7340a300a0369626312290a2708b891c7341220e09159530585455058cf1785f411ea44230f39334e6e0f6a3c54dbf069df2b620a300a03676f7612290a2708b891c7341220db85ddd37470983b14186e975a175dfb0bf301b43de685ced0aef18d28b4e0420a320a05706169727312290a2708b891c7341220a78b556bc9e73d86b4c63ceaf146db71b12ac80e4c10dd0ce6eb09c99b0c7cfe0a360a0974696d655f6c6f636b12290a2708b891c73412204775dbe01d41cab018c21ba5c2af94720e4d7119baf693670e70a40ba2a52143")
+	// Bytest1 is the inputs of exploit tx 0xebf83628ba893d35b496121fb8201666b8e09f3cbadf0e269162baa72efe3b8b
+	bytest2, _ := hex.DecodeString("00000000000000000000000000000000000000000000000000000000000005086962630000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000e00000100380200000000010dd85c0000000000000000000000000000000000000000000000000000000000000093000000000000000000000000000000000000000000000000000000000000000000f870a0424e4200000000000000000000000000000000000000000000000000000000009400000000000000000000000000000000000000008ad3c21bcecceda100000094489a8756c18c0b8b24ec2a2b9ff3d4d447f79bec94489a8756c18c0b8b24ec2a2b9ff3d4d447f79bec846553f10072cda827a83531ca0fd7ac917a6b65649719aab0836722caafe0603147a523180a8d020a066961766c3a76120e00000100380200000000010dd85c1af201f0010aed010a2b0802100318b091c73422200c10f902d266c238a4ca9e26fa9bc36483cd3ebee4e263012f5e7f40c22ee4d20a4d0801100218b091c7342220e4fd47bffd1c06e67edad92b2bf9ca63631978676288a2aa99f95c459436ef632a20da657c1ffb86c684eb3e265361ef0fa4f9dfa670b45f9f91c5eb6ad84b21a4d112001a370a0e0000010038020000000000000002122011056c6919f02d966991c10721684a8d1542e44003f9ffb47032c18995d4ac7f18b091c7341a340a0e00000100380200000000010dd85c12202c3a561458f8527b002b5ec3cab2d308662798d6245d4588a4e6a80ebdfe30ac18010ad4050a0a6d756c746973746f726512036962631ac005be050abb050a110a066f7261636c6512070a0508b891c7340a0f0a046d61696e12070a0508b891c7340a350a08736c617368696e6712290a2708b891c7341220c8ccf341e6e695e7e1cb0ce4bf347eea0cc16947d8b4e934ec400b57c59d6f860a380a0b61746f6d69635f7377617012290a2708b891c734122042d4ecc9468f71a70288a95d46564bfcaf2c9f811051dcc5593dbef152976b010a110a0662726964676512070a0508b891c7340a300a0364657812290a2708b891c73412201773be443c27f61075cecdc050ce22eb4990c54679089e90afdc4e0e88182a230a2f0a02736312290a2708b891c7341220df7a0484b7244f76861b1642cfb7a61d923794bd2e076c8dbd05fc4ee29f3a670a330a06746f6b656e7312290a2708b891c734122064958c2f76fec1fa5d1828296e51264c259fa264f499724795a740f48fc4731b0a320a057374616b6512290a2708b891c734122015d2c302143bdf029d58fe381cc3b54cedf77ecb8834dfc5dc3e1555d68f19ab0a330a06706172616d7312290a2708b891c734122050abddcb7c115123a5a4247613ab39e6ba935a3d4f4b9123c4fedfa0895c040a0a300a0361636312290a2708b891c734122079fb5aecc4a9b87e56231103affa5e515a1bdf3d0366490a73e087980b7f1f260a0e0a0376616c12070a0508b891c7340a300a0369626312290a2708b891c7341220e09159530585455058cf1785f411ea44230f39334e6e0f6a3c54dbf069df2b620a300a03676f7612290a2708b891c7341220db85ddd37470983b14186e975a175dfb0bf301b43de685ced0aef18d28b4e0420a320a05706169727312290a2708b891c7341220a78b556bc9e73d86b4c63ceaf146db71b12ac80e4c10dd0ce6eb09c99b0c7cfe0a360a0974696d655f6c6f636b12290a2708b891c73412204775dbe01d41cab018c21ba5c2af94720e4d7119baf693670e70a40ba2a52143")
+
+	for _, bytest := range [][]byte{bytest1, bytest2} {
+		validator := iavlMerkleProofValidate{}
+		res, err := validator.Run(bytest)
+		assert.NoError(t, err)
+		assert.Equal(t, res[len(res)-1], uint8(1))
+
+		moranValidator := iavlMerkleProofValidateMoran{}
+		res, err = moranValidator.Run(bytest)
+		assert.Errorf(t, err, "invalid merkle proof")
+		assert.Nil(t, res)
+	}
+}
+
+func TestAbsenceMerkleProofValidateMoran(t *testing.T) {
+	// Bytest contains absence op
+	bytest, _ := hex.DecodeString("00000000000000000000000000000000000000000000000000000000000007306163630000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001c6163636f756e743a8a4e2eb018bdf98a8f53ec755740ffc728637a1d000000000000000000000000000000000000000000000000000000000000007b4bdc4c270a750a148a4e2eb018bdf98a8f53ec755740ffc728637a1d12110a0941544348412d3733301080f69bf321120b0a03424e4210e8baeb8d44120f0a075050432d303041108094ebdc031a26eb5ae98721031c199c92e5b0080967da99be27cf2da53317441b4a663e6d9c6caf02be1fdbdc20d7962b28152c69c314b4de5c8035253c8bc0771d9ca17b1b23a57c0c6d068b57579791cae20add070a066961766c3a61121c6163636f756e743a8a4e2eb018bdf98a8f53ec755740ffc728637a1d1ab407b2070aaf070a2d081810cdfd2b188096a82222209f223f804e2d94ac51c4321b0687397012e6d95eb9783b03bc790da631004c7c0a2d081710adb31a18f395a8222a20d2a38865de82383ccce0140513b65cec1bf2ae6cd7dfeb22eb6faadb4e26b26f0a2d081510b2990b18f395a82222208a02bbd5a695dfc772627ac8744aa9cf30ae26575bdce8c96a9a0d0999175b430a2d081410e6ff0418f395a8222a20d39619c779be909e67f23499fb74eb2c19afd7f21523401d4ccf7e917db5cd600a2d081210e3fe0118f395a8222a20a10cc73843f889d9e03a463eb135e928bb980e19734344cba0fbf4e8a4c5258b0a2c081010dd6518f395a8222a2007fd15843a2fd3f58d021b0e072a6c70742d7a3d993a922445e3491e1c14ee8e0a2c080f10cc2a18eda6a7222a20088942d7b30abd021d8e9505cc41313fad87c8c10a799f3b51018b7b2cfe4ad90a2c080d10b70d18eda6a7222a2091a37bc44d0c61e3752ddc59eb390355ab65e8a9fb453be4f0acec537f1ca14f0a2c080c10890818eda6a72222201cfc317855a06667c45812fe36efe33af05671dfe0d9b56b02662011af2e79e30a2c080b10ac0318c4b0ee212220aeb454a4b3243b6269a2fd8841dca9a951c53b30f1e27da91063dae7224402c70a2c080910e40118c4b0ee212a20441340a4de6498f861b97b3f3ad9603af055e5af51a0d96fff2ae28e3c5c6c9a0a2c0808108d0118c4b0ee212220ae32ea4b9ab7b53571da320e2815fd8b2c278124961cca4a1849a799842424450a2b0807104d18c4b0ee212220e2804c9b7f045ec0b4ab20920a937b82fda8b7a9ddd12b21637335b915cfda550a2b0806102418a5f4c7192a20ec85f22addedfc82c771af5b4c77544b7c1d7c5bbac33f2712dfba1045ebdbd00a2b0805101118a5f4c7192a2071ade34dcc447a0ba8adc603080633d15c06f3525830c86ebce35eca0a4921fc0a2b0804100c18a5f4c7192a205190bce93993e65b266a3417ed511df8897a812cb4b62569e5afcfbec10b69cd0a2b0803100618a5f4c7192220b76c6884f1d412ac10bfb3987fb7d26f0330b2a85539509ebc5c6bdec2f95d520a2b0802100418a5f4c71922206a285b4a4f9d1c687bbafa1f3649b6a6e32b1a85dd0402421210683e846cf0020a2b0801100218a5f4c7192220033b3f7c6dcb258b6e55545e7a4f51539447cd595eb8a2e373ba0015502da1051a450a1c6163636f756e743a8a4e2eb018bdf98a8f53ec755740ffc728637a1d12201a272295e94cf1d8090bdb019dde48e9dab026ad2c3e43aaa7e61cc954a9245d18a5f4c7190ab6040a0a6d756c746973746f726512036163631aa204a0040a9d040a300a0364657812290a27088496a822122038fc49f49648fec62acc434151a51eaa378c1b20a730a749548e36f1529422500a300a03676f7612290a27088496a8221220a78ce489bdf08b9ee869c184876e1623dc38b3e64a5cf1a0005f97976c64deac0a380a0b61746f6d69635f7377617012290a27088496a8221220544c2fa38f61e10a39ec00b3e724d5834761268bb455cdbf5843bcf1531f8fbc0a300a0376616c12290a27088496a82212201f71082c9f6f45fb456b2c00b41e50d2f662f2dfec3cb6965f19d214bf02f3980a0f0a046d61696e12070a05088496a8220a320a057374616b6512290a27088496a82212200dd467343c718f240e50b4feac42970fc8c1c69a018be955f9c27913ac1f8b3c0a300a0361636312290a27088496a8221220270c19ccc9c40c5176b3dfbd8af734c97a307e0dbd8df9e286dcd5d709f973ed0a330a06746f6b656e7312290a27088496a8221220c4f96eedf50c83964de9df013afec2e545012d92528b643a5166c828774187b60a320a05706169727312290a27088496a8221220351c55cfda84596ecd22ebc77013662aba97f81f19d9ef3d150213bb07c823060a360a0974696d655f6c6f636b12290a27088496a8221220e7adf5bd30ce022decf0e9341bf05c464ed70cdbc97423bd2bab8f3571e5179b0a330a06706172616d7312290a27088496a822122042a9dfc356ca435db131eb41fb1975c8482f2434537918665e530b0b4633b5f9")
+	moranValidator := iavlMerkleProofValidateMoran{}
+	res, err := moranValidator.Run(bytest)
+	assert.Errorf(t, err, "invalid merkle proof")
+	assert.Nil(t, res)
+}
+
+func TestMultiStore(t *testing.T) {
+	goodProof := lightclient.NewMultiStoreProofOp([]byte("legit"), &lightclient.MultiStoreProof{
+		StoreInfos: []lightclient.StoreInfo{
+			{
+				Name: "legit",
+				Core: lightclient.StoreCore{
+					CommitID: lightclient.CommitID{
+						Version: 1,
+						Hash:    []byte("legithash"),
+					},
+				},
+			},
+		},
+	})
+
+	result1, err := goodProof.Run([][]byte{[]byte("legithash")})
+	assert.NoError(t, err)
+
+	_, err = goodProof.Run([][]byte{[]byte("evilhash")})
+	assert.Error(t, err, "hash mismatch for substore")
+
+	badProof := lightclient.NewMultiStoreProofOp([]byte("legit"), &lightclient.MultiStoreProof{
+		StoreInfos: []lightclient.StoreInfo{
+			{
+				Name: "legit",
+				Core: lightclient.StoreCore{
+					CommitID: lightclient.CommitID{
+						Version: 1,
+						Hash:    []byte("evilhash"),
+					},
+				},
+			},
+			{
+				Name: "legit",
+				Core: lightclient.StoreCore{
+					CommitID: lightclient.CommitID{
+						Version: 1,
+						Hash:    []byte("legithash"),
+					},
+				},
+			},
+		},
+	})
+
+	_, err = badProof.Run([][]byte{[]byte("legithash")})
+	assert.Error(t, err, "hash mismatch for substore")
+
+	result2, err := badProof.Run([][]byte{[]byte("evilhash")})
+	assert.NoError(t, err)
+	assert.Equal(t, result1, result2)
+
+	err = multiStoreOpVerifier(badProof)
+	assert.Error(t, err, "duplicated store")
 }
```

### core/vm/evm.go
```diff
@@ -51,6 +51,8 @@ type (
 func (evm *EVM) precompile(addr common.Address) (PrecompiledContract, bool) {
 	var precompiles map[common.Address]PrecompiledContract
 	switch {
+	case evm.chainRules.IsMoran:
+		precompiles = PrecompiledContractsIsMoran
 	case evm.chainRules.IsNano:
 		precompiles = PrecompiledContractsIsNano
 	case evm.chainRules.IsBerlin:
```

### core/vm/lightclient/types.go
```diff
@@ -215,6 +215,12 @@ type KeyValueMerkleProof struct {
 	StoreName string
 	AppHash   []byte
 	Proof     *merkle.Proof
+
+	verifiers []merkle.ProofOpVerifier
+}
+
+func (kvmp *KeyValueMerkleProof) SetVerifiers(verifiers []merkle.ProofOpVerifier) {
+	kvmp.verifiers = verifiers
 }
 
 func (kvmp *KeyValueMerkleProof) Validate() bool {
@@ -225,11 +231,11 @@ func (kvmp *KeyValueMerkleProof) Validate() bool {
 	kp = kp.AppendKey(kvmp.Key, merkle.KeyEncodingURL)
 
 	if len(kvmp.Value) == 0 {
-		err := prt.VerifyAbsence(kvmp.Proof, kvmp.AppHash, kp.String())
+		err := prt.VerifyAbsence(kvmp.Proof, kvmp.AppHash, kp.String(), kvmp.verifiers...)
 		return err == nil
 	}
 
-	err := prt.VerifyValue(kvmp.Proof, kvmp.AppHash, kp.String(), kvmp.Value)
+	err := prt.VerifyValue(kvmp.Proof, kvmp.AppHash, kp.String(), kvmp.Value, kvmp.verifiers...)
 	return err == nil
 }
 
```

### eth/protocols/snap/sync.go
```diff
@@ -169,7 +169,7 @@ type bytecodeResponse struct {
 // to actual requests and to validate any security constraints.
 //
 // Concurrency note: storage requests and responses are handled concurrently from
-// the main runloop to allow Merkel proof verifications on the peer's thread and
+// the main runloop to allow Merkle proof verifications on the peer's thread and
 // to drop on invalid response. The request struct must contain all the data to
 // construct the response without accessing runloop internals (i.e. tasks). That
 // is only included to allow the runloop to match a response to the task being
```

### go.mod
```diff
@@ -71,7 +71,7 @@ require (
 	github.com/syndtr/goleveldb v1.0.1-0.20210819022825-2ae1ddf74ef7
 	github.com/tendermint/go-amino v0.14.1
 	github.com/tendermint/iavl v0.12.0
-	github.com/tendermint/tendermint v0.31.11
+	github.com/tendermint/tendermint v0.31.12
 	github.com/tklauser/go-sysconf v0.3.5 // indirect
 	github.com/tyler-smith/go-bip39 v1.0.1-0.20181017060643-dbb3b84ba2ef
 	go.etcd.io/bbolt v1.3.5 // indirect
@@ -90,4 +90,5 @@ require (
 replace (
 	github.com/gogo/protobuf v1.1.1 => github.com/gogo/protobuf v1.3.2
 	github.com/gogo/protobuf v1.3.1 => github.com/gogo/protobuf v1.3.2
+	github.com/tendermint/tendermint => github.com/bnb-chain/tendermint v0.31.12
 )
```

### go.sum
```diff
@@ -79,6 +79,8 @@ github.com/beorn7/perks v0.0.0-20180321164747-3a771d992973/go.mod h1:Dwedo/Wpr24
 github.com/beorn7/perks v1.0.0 h1:HWo1m869IqiPhD389kmkxeTalrjNbbJTC8LXupb+sl0=
 github.com/beorn7/perks v1.0.0/go.mod h1:KWe93zE9D1o94FZ5RNwFwVgaQK1VOXiVxmqh+CedLV8=
 github.com/bmizerany/pat v0.0.0-20170815010413-6226ea591a40/go.mod h1:8rLXio+WjiTceGBHIoTvn60HIbs7Hm7bcHjyrSqYB9c=
+github.com/bnb-chain/tendermint v0.31.12 h1:g+blWaXkRw6iHa56lcRfRzPXHgURCWPmgIvaGBSV7Zc=
+github.com/bnb-chain/tendermint v0.31.12/go.mod h1:j6XU7CArrhQ+9XBMRwdIz63iUxdVwSrZ8f7vP7gcCqg=
 github.com/boltdb/bolt v1.3.1/go.mod h1:clJnj/oiGkjum5o1McbSZDSLxVThjynRyGBgiAx27Ps=
 github.com/btcsuite/btcd v0.20.1-beta h1:Ik4hyJqN8Jfyv3S4AGBOmyouMsYE3EdYODkMbQjwPGw=
 github.com/btcsuite/btcd v0.20.1-beta/go.mod h1:wVuoA8VJLEcwgqHBwHmzLRazpKxTv13Px/pDuV7OomQ=
@@ -429,8 +431,6 @@ github.com/tendermint/go-amino v0.14.1 h1:o2WudxNfdLNBwMyl2dqOJxiro5rfrEaU0Ugs6o
 github.com/tendermint/go-amino v0.14.1/go.mod h1:i/UKE5Uocn+argJJBb12qTZsCDBcAYMbR92AaJVmKso=
 github.com/tendermint/iavl v0.12.0 h1:xcaFAr+ycqCj7WN1RzL2EfcBioRDOHcU1oWcg83K028=
 github.com/tendermint/iavl v0.12.0/go.mod h1:EoKMMv++tDOL5qKKVnoIqtVPshRrEPeJ0WsgDOLAauM=
-github.com/tendermint/tendermint v0.31.11 h1:TIs//4WfEAG4TOZc2eUfJPI3T8KrywXQCCPnGAaM1Wo=
-github.com/tendermint/tendermint v0.31.11/go.mod h1:ymcPyWblXCplCPQjbOYbrF1fWnpslATMVqiGgWbZrlc=
 github.com/tinylib/msgp v1.0.2/go.mod h1:+d+yLhGm8mzTaHzB+wgMYrodPfmZrzkirds8fDWklFE=
 github.com/tklauser/go-sysconf v0.3.5 h1:uu3Xl4nkLzQfXNsWn15rPc/HQCJKObbt1dKJeWp3vU4=
 github.com/tklauser/go-sysconf v0.3.5/go.mod h1:MkWzOF4RMCshBAMXuhXJs64Rte09mITnppBXY/rYEFI=
@@ -534,7 +534,6 @@ golang.org/x/sync v0.0.0-20181221193216-37e7f081c4d4/go.mod h1:RxMgew5VJxzue5/jJ
 golang.org/x/sync v0.0.0-20190227155943-e225da77a7e6/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20190423024810-112230192c58/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20190911185100-cd5d95a43a6e/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
-golang.org/x/sync v0.0.0-20200317015054-43a5402ce75a/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20201020160332-67f06af15bc9/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20210220032951-036812b2e83c h1:5KslGYwFpkhGh+Q16bwMP3cOontH8FOep7tGV86Y7SQ=
 golang.org/x/sync v0.0.0-20210220032951-036812b2e83c/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
```
