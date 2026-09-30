# [?] Guard against buffer overflow in verifyCOAOwnershipProof precompiled call

## Summary
Severity: Unknown
Chain: Flow
Component: onflow/flow-go
Published: 2026-01-20
Source: https://github.com/onflow/flow-go/commit/30f1f35c923446c077d24c9ef252884881778213
Type: security-commit

## Details
Guard against buffer overflow in verifyCOAOwnershipProof precompiled call

## Patch
### fvm/evm/evm_test.go
```diff
@@ -4062,6 +4062,105 @@ func TestCadenceArch(t *testing.T) {
 				require.Error(t, output.Err)
 			})
 	})
+
+	t.Run("testing calling Cadence arch - COA ownership proof (buffer overflow)", func(t *testing.T) {
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
@@ -158,11 +158,16 @@ func ReadBytes(buffer []byte, index int) ([]byte, error) {
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
@@ -172,6 +177,10 @@ func ReadBytes(buffer []byte, index int) ([]byte, error) {
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
