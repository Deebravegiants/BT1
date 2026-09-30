# [?] rpc: fix non-deterministic error in eth_simulateV1 state override (#21382)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-05-24
Source: https://github.com/erigontech/erigon/commit/2d11f996c5e3da3ce0820fe3297611e8bf2ca9ff
Type: security-commit

## Details
rpc: fix non-deterministic error in eth_simulateV1 state override (#21382)

Sort override addresses once before both loops so map iteration order
never affects error messages or precompile-move semantics. Add nil guard
for precompiles map and test coverage for the MovePrecompileTo success
path.
Tests Re-enabled:
* eth_simulateV1/test_201 and 
* eth_createAccessList/test_15 (the code is already OK after PR #21086 )

Co-authored-by: Claude Sonnet 4.6 <noreply@anthropic.com>

## Patch
### .github/workflows/scripts/run_rpc_tests_ethereum.sh
```diff
@@ -30,8 +30,6 @@ DISABLED_TEST_LIST=(
   eth_coinbase/test_01.json
   eth_createAccessList/test_16.json
   eth_getTransactionByHash/test_02.json
-  # Temporarily disabled: test is flaky and fails non-deterministically; needs investigation
-  eth_simulateV1/test_201.json
   # Small prune issue that leads to wrong ReceiptDomain data at 16999999 (probably at every million) block: https://github.com/erigontech/erigon/issues/13050
   ots_searchTransactionsBefore/test_04.tar
   # Temporary disable required block 23917742
@@ -47,7 +45,6 @@ DISABLED_TEST_LIST=(
   web3_clientVersion/test_1.json
   # Temporarily disabled: the following tests hang (possible regression in Erigon).
   # For debug_traceTransaction, the issue is under analysis.
-  eth_createAccessList/test_15.json
   debug_traceTransaction/test_12.json
   # Temporarily disabled: the following tests: ots_searchTransactionsAfter/test_11.json, ots_searchTransactionsAfter/test_12.json have been disabled because their response changed after moving the TIP. The request or the response should be updated so that the output is unaffected by changes to the TIP
   ots_searchTransactionsAfter/test_11.json
```

### rpc/ethapi/state_overrides.go
```diff
@@ -17,9 +17,11 @@
 package ethapi
 
 import (
+	"bytes"
 	"errors"
 	"fmt"
 	"math/big"
+	"sort"
 
 	"github.com/holiman/uint256"
 
@@ -32,8 +34,9 @@ import (
 
 type StateOverrides map[accounts.Address]Account
 
-func (so *StateOverrides) override(ibs *state.IntraBlockState) error {
-	for addr, account := range *so {
+func (so *StateOverrides) override(ibs *state.IntraBlockState, addrs []accounts.Address) error {
+	for _, addr := range addrs {
+		account := (*so)[addr]
 		// Override account nonce.
 		if account.Nonce != nil {
 			if err := ibs.SetNonce(addr, uint64(*account.Nonce), tracing.NonceChangeUnspecified); err != nil {
@@ -85,13 +88,28 @@ func (so *StateOverrides) override(ibs *state.IntraBlockState) error {
 }
 
 func (so *StateOverrides) Override(ibs *state.IntraBlockState, precompiles vm.PrecompiledContracts, rules *chain.Rules) error {
-	err := so.override(ibs)
+	if precompiles == nil {
+		precompiles = make(vm.PrecompiledContracts)
+	}
+	// Sort addresses for deterministic iteration order across both loops (map iteration is random in Go).
+	addrs := make([]accounts.Address, 0, len(*so))
+	for addr := range *so {
+		addrs = append(addrs, addr)
+	}
+	sort.Slice(addrs, func(i, j int) bool {
+		ai, aj := addrs[i].Value(), addrs[j].Value()
+		return bytes.Compare(ai[:], aj[:]) < 0
+	})
+
+	err := so.override(ibs, addrs)
 	if err != nil {
 		return err
 	}
+
 	// Tracks destinations of precompiles that were moved.
 	dirtyAddresses := make(map[accounts.Address]struct{})
-	for addr, account := range *so {
+	for _, addr := range addrs {
+		account := (*so)[addr]
 		// If a precompile was moved to this address already, it can't be overridden.
 		if _, ok := dirtyAddresses[addr]; ok {
 			return fmt.Errorf("account %s has already been overridden by a precompile", addr)
```

### rpc/ethapi/state_overrides_test.go
```diff
@@ -0,0 +1,66 @@
+package ethapi
+
+import (
+	"fmt"
+	"testing"
+
+	"github.com/stretchr/testify/require"
+
+	"github.com/erigontech/erigon/common"
+	"github.com/erigontech/erigon/execution/chain"
+	"github.com/erigontech/erigon/execution/state"
+	"github.com/erigontech/erigon/execution/types/accounts"
+	"github.com/erigontech/erigon/execution/vm"
+)
+
+type stubPrecompile struct{ name string }
+
+func (s stubPrecompile) RequiredGas([]byte) uint64  { return 0 }
+func (s stubPrecompile) Run([]byte) ([]byte, error) { return nil, nil }
+func (s stubPrecompile) Name() string               { return s.name }
+
+// TestStateOverrides_MovePrecompileDeterministicError verifies that when multiple
+// non-precompile accounts carry MovePrecompileToAddress, the error always names
+// the lexicographically smallest address rather than a random one from map iteration.
+func TestStateOverrides_MovePrecompileDeterministicError(t *testing.T) {
+	addr1 := common.HexToAddress("0x0100000000000000000000000000000000000000")
+	addr2 := common.HexToAddress("0x0200000000000000000000000000000000000000")
+	target := common.HexToAddress("0xc200000000000000000000000000000000000000")
+
+	so := StateOverrides{
+		accounts.InternAddress(addr1): Account{MovePrecompileTo: &target},
+		accounts.InternAddress(addr2): Account{MovePrecompileTo: &target},
+	}
+
+	want := fmt.Sprintf("account %s is not a precompile", addr1)
+
+	for i := 0; i < 500; i++ {
+		ibs := state.New(state.NewNoopReader())
+		err := so.Override(ibs, vm.PrecompiledContracts{}, &chain.Rules{})
+		require.EqualError(t, err, want, "iteration %d: error must be deterministic", i)
+	}
+}
+
+func TestStateOverrides_MovePrecompileSuccess(t *testing.T) {
+	srcAddr := common.HexToAddress("0x0000000000000000000000000000000000000001")
+	dstAddr := common.HexToAddress("0xd000000000000000000000000000000000000001")
+
+	src := accounts.InternAddress(srcAddr)
+	dst := accounts.InternAddress(dstAddr)
+	stub := stubPrecompile{name: "ecrecover"}
+
+	so := StateOverrides{
+		src: Account{MovePrecompileTo: &dstAddr},
+	}
+
+	precompiles := vm.PrecompiledContracts{src: stub}
+	ibs := state.New(state.NewNoopReader())
+	err := so.Override(ibs, precompiles, &chain.Rules{})
+	require.NoError(t, err)
+
+	_, atSrc := precompiles[src]
+	got, atDst := precompiles[dst]
+	require.False(t, atSrc, "precompile must be removed from source")
+	require.True(t, atDst, "precompile must be present at destination")
+	require.Equal(t, stub.Name(), got.Name())
+}
```
