# [?] Merge pull request #8357 from onflow/mpeter/fix-cadence-arch-buffer-overflow

## Summary
Severity: Unknown
Chain: Flow
Component: onflow/flow-go
Published: 2026-01-22
Source: https://github.com/onflow/flow-go/commit/46b6f9add149c36d7f43447f01acdcb847b45a7b
Type: security-commit

## Details
Merge pull request #8357 from onflow/mpeter/fix-cadence-arch-buffer-overflow

[Flow EVM] Check for integer overflow when reading ABI encoded bytes

## Patch
### fvm/evm/evm_test.go
```diff
@@ -4062,6 +4062,105 @@ func TestCadenceArch(t *testing.T) {
 				require.Error(t, output.Err)
 			})
 	})
+
+	t.Run("testing calling Cadence arch - COA ownership proof (index overflow)", func(t *testing.T) {
+		chain := flow.Emulator.Chain()
+		sc := systemcontracts.SystemContractsForChain(chain.ChainID())
+		RunWithNewEnvironment(t,
+			chain, func(
+				ctx fvm.Context,
+				vm fvm.VM,
+				snapshot snapshot.SnapshotTree,
+				testContract *TestContract,
+				testAccount *EOATestAccount,
+			) {
+				code := []byte(fmt.Sprintf(
+					`
+					import EVM from %s
+
+					transaction {
+						let coa: @EVM.CadenceOwnedAccount
+
+						prepare(signer: auth(Storage) &Account) {
+							self.coa <- EVM.createCadenceOwnedAccount()
+						}
+
+						execute {
+							let cadenceArchAddress = EVM.EVMAddress(
+								bytes: [
+									0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
+									0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01
+								]
+							)
+
+							var calldata: [UInt8] = []
+
+							// Function selector for verifyCOAOwnershipProof = 0x5ee837e7
+							calldata = calldata.concat([0x5e, 0xe8, 0x37, 0xe7])
+
+							// Address parameter (32 bytes)
+							var i = 0
+							while i < 31 { calldata = calldata.concat([0x00]); i = i + 1 }
+							calldata = calldata.concat([0x01])
+
+							// bytes32 parameter (32 bytes)
+							i = 0
+							while i < 32 { calldata = calldata.concat([0x00]); i = i + 1 }
+
+							// MALICIOUS offset: 0x7FFFFFFFFFFFFFFF (MaxInt64)
+							// When ReadBytes does: index + 32, this overflows to negative
+							// MaxInt64 + 32 = -9223372036854775777 (wraps around)
+							i = 0
+							while i < 24 { calldata = calldata.concat([0x00]); i = i + 1 }
+							calldata = calldata.concat([0x7F]) // High byte = 0x7F
+							calldata = calldata.concat([0xFF])
+							calldata = calldata.concat([0xFF])
+							calldata = calldata.concat([0xFF])
+							calldata = calldata.concat([0xFF])
+							calldata = calldata.concat([0xFF])
+							calldata = calldata.concat([0xFF])
+							calldata = calldata.concat([0xFF]) // = 0x7FFFFFFFFFFFFFFF
+
+							// Length (32 bytes)
+							i = 0
+							while i < 31 { calldata = calldata.concat([0x00]); i = i + 1 }
+							calldata = calldata.concat([0x20])
+
+							// Dummy data (32 bytes)
+							i = 0
+							while i < 32 { calldata = calldata.concat([0x00]); i = i + 1 }
+
+							let result = self.coa.call(
+								to: cadenceArchAddress,
+								data: calldata,
+								gasLimit: 100_000,
+								value: EVM.Balance(attoflow: 0)
+							)
+							assert(result.status == EVM.Status.failed, message: "unexpected status")
+							assert(result.errorMessage == "input data is too small for decoding", message: result.errorMessage)
+
+							destroy self.coa
+						}
+					}
+					`,
+					sc.EVMContract.Address.HexWithPrefix(),
+				))
+
+				txBody, err := flow.NewTransactionBodyBuilder().
+					SetScript(code).
+					SetPayer(sc.FlowServiceAccount.Address).
+					AddAuthorizer(sc.FlowServiceAccount.Address).
+					Build()
+				require.NoError(t, err)
+
+				tx := fvm.Transaction(txBody, 0)
+
+				_, output, err := vm.Run(ctx, tx, snapshot)
+				require.NoError(t, err)
+				require.NoError(t, output.Err)
+			},
+		)
+	})
 }
 
 func TestNativePrecompiles(t *testing.T) {
```

### fvm/evm/precompiles/abi.go
```diff
@@ -8,6 +8,22 @@ import (
 	gethCommon "github.com/ethereum/go-ethereum/common"
 )
 
+// The Cadence Arch precompiled contract that is injected in the EVM environment,
+// implements the following functions:
+// - `flowBlockHeight()`
+// - `revertibleRandom()`
+// - `getRandomSource(uint64)`
+// - `verifyCOAOwnershipProof(address,bytes32,bytes)`
+//
+// By design, all errors that are the result of user input, will be propagated
+// in the EVM environment, and can be handled by developers, as they see fit.
+// However, all FVM fatal errors, will cause a panic and abort the outer Cadence
+// transaction. The reason behind this is that we want to have visibility when
+// such special errors occur. This way, any potential bugs will not go unnoticed.
+// The Cadence runtime recovers any Go crashers (index out of bounds, nil
+// dereferences, etc.) and fails the transaction gracefully, so a panic in the
+// precompiled contract does not indicate a node/runtime crash.
+
 // This package provides fast and efficient
 // utilities needed for abi encoding and decoding
 // encodings are mostly used for testing purpose
@@ -30,9 +46,11 @@ const (
 	EncodedUint256Size = FixedSizeUnitDataReadSize
 )
 
-var ErrInputDataTooSmall = errors.New("input data is too small for decoding")
-var ErrBufferTooSmall = errors.New("buffer too small for encoding")
-var ErrDataTooLarge = errors.New("input data is too large for encoding")
+var (
+	ErrInputDataTooSmall = errors.New("input data is too small for decoding")
+	ErrBufferTooSmall    = errors.New("buffer too small for encoding")
+	ErrDataTooLarge      = errors.New("input data is too large for encoding")
+)
 
 // ReadAddress reads an address from the buffer at index
 func ReadAddress(buffer []byte, index int) (gethCommon.Address, error) {
@@ -158,11 +176,16 @@ func ReadBytes(buffer []byte, index int) ([]byte, error) {
 	if len(buffer) < index+EncodedUint64Size {
 		return nil, ErrInputDataTooSmall
 	}
+
 	// reading offset (we read into uint64) and adjust index
 	offset, err := ReadUint64(buffer, index)
 	if err != nil {
 		return nil, err
 	}
+	if offset > uint64(len(buffer)) {
+		return nil, ErrInputDataTooSmall
+	}
+
 	index = int(offset)
 	if len(buffer) < index+EncodedUint64Size {
 		return nil, ErrInputDataTooSmall
@@ -172,6 +195,10 @@ func ReadBytes(buffer []byte, index int) ([]byte, error) {
 	if err != nil {
 		return nil, err
 	}
+	if length > uint64(len(buffer)) {
+		return nil, ErrInputDataTooSmall
+	}
+
 	index += EncodedUint64Size
 	if len(buffer) < index+int(length) {
 		return nil, ErrInputDataTooSmall
```

### fvm/evm/precompiles/arch.go
```diff
@@ -6,6 +6,22 @@ import (
 	"github.com/onflow/flow-go/fvm/evm/types"
 )
 
+// The Cadence Arch precompiled contract that is injected in the EVM environment,
+// implements the following functions:
+// - `flowBlockHeight()`
+// - `revertibleRandom()`
+// - `getRandomSource(uint64)`
+// - `verifyCOAOwnershipProof(address,bytes32,bytes)`
+//
+// By design, all errors that are the result of user input, will be propagated
+// in the EVM environment, and can be handled by developers, as they see fit.
+// However, all FVM fatal errors, will cause a panic and abort the outer Cadence
+// transaction. The reason behind this is that we want to have visibility when
+// such special errors occur. This way, any potential bugs will not go unnoticed.
+// The Cadence runtime recovers any Go crashers (index out of bounds, nil
+// dereferences, etc.) and fails the transaction gracefully, so a panic in the
+// precompiled contract does not indicate a node/runtime crash.
+
 const CADENCE_ARCH_PRECOMPILE_NAME = "CADENCE_ARCH"
 
 var (
```
