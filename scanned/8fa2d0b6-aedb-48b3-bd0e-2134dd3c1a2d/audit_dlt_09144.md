# [?] fix: add selectors config and fix analyze error possible panic (#17544)

## Summary
Severity: Unknown
Chain: Chainlink
Component: smartcontractkit/chainlink
Published: 2025-05-01
Source: https://github.com/smartcontractkit/chainlink/commit/b70577803d4e1c8a1660383b293d44b454d1363b
Type: security-commit

## Details
fix: add selectors config and fix analyze error possible panic (#17544)

## Patch
### deployment/common/changeset/mcms_firedrill.go
```diff
@@ -17,6 +17,7 @@ import (
 
 type FireDrillConfig struct {
 	TimelockCfg proposalutils.TimelockConfig
+	Selectors   []uint64
 }
 
 // buildNoOPEVM builds a dummy tx that transfers 0 to the RBACTimelock
@@ -71,7 +72,10 @@ func buildNoOPSolana() (mcmstypes.Transaction, error) {
 // It is used to make sure team member can effectively sign proposal and that the execution pipelines are healthy.
 // The changeset will create a NO-OP transaction for each chain selector in the environment and create a proposal for it.
 func MCMSSignFireDrillChangeset(e deployment.Environment, cfg FireDrillConfig) (deployment.ChangesetOutput, error) {
-	allSelectors := e.AllChainSelectors()
+	allSelectors := cfg.Selectors
+	if len(allSelectors) == 0 {
+		allSelectors = e.AllChainSelectors()
+	}
 	operations := make([]mcmstypes.BatchOperation, 0, len(allSelectors))
 	timelocks := map[uint64]string{}
 	mcmAddresses := map[uint64]string{}
```

### deployment/common/changeset/mcms_firedrill_test.go
```diff
@@ -47,6 +47,8 @@ func setupFiredrillTestEnv(t *testing.T) deployment.Environment {
 func TestMCMSSignFireDrillChangeset(t *testing.T) {
 	t.Parallel()
 	env := setupFiredrillTestEnv(t)
+	chainSelector := env.AllChainSelectors()[0]
+	chainSelector2 := env.AllChainSelectors()[1]
 	// Add the timelock as a signer to check state changes
 	for _, tc := range []struct {
 		name       string
@@ -59,6 +61,7 @@ func TestMCMSSignFireDrillChangeset(t *testing.T) {
 					commonchangeset.Configure(
 						deployment.CreateLegacyChangeSet(commonchangeset.MCMSSignFireDrillChangeset),
 						commonchangeset.FireDrillConfig{
+							Selectors: []uint64{chainSelector, chainSelector2},
 							TimelockCfg: proposalutils.TimelockConfig{
 								MCMSAction: mcmsTypes.TimelockActionBypass,
 							},
```

### deployment/common/proposalutils/analyze.go
```diff
@@ -230,6 +230,9 @@ func NewTxCallDecoder(extraAnalyzers []Analyzer) *TxCallDecoder {
 }
 
 func (p *TxCallDecoder) Analyze(address string, abi *abi.ABI, data []byte) (*DecodedCall, error) {
+	if len(data) < 4 {
+		return nil, fmt.Errorf("data with value %s is too short", hexutil.Encode(data))
+	}
 	methodID, methodData := data[:4], data[4:]
 	method, err := abi.MethodById(methodID)
 	if err != nil {
```
