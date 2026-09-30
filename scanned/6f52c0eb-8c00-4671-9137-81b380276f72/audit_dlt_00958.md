# [?] fix race condition in deployment vs query (#22713)

## Summary
Severity: Unknown
Chain: Chainlink
Component: smartcontractkit/chainlink
Published: 2026-06-03
Source: https://github.com/smartcontractkit/chainlink/commit/5401ad107fce1d68b2a0e61c24aec1b3caa8cceb
Type: security-commit

## Details
fix race condition in deployment vs query (#22713)

* fix race condition in deployment vs query

* Apply suggestions from code review

Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

---------

Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

## Patch
### deployment/ccip/changeset/testhelpers/test_helpers_solana_v0_1_0.go
```diff
@@ -1474,6 +1474,15 @@ func deploySingleFeed(
 
 	lggr.Infow("deployed mockTokenFeed", "addr", mockTokenFeed.Address)
 
+	ctx := chain.DeployerKey.Context
+	if ctx == nil {
+		ctx = context.Background()
+	}
+	if err := shared.WaitForContractCode(ctx, chain.Client, mockTokenFeed.Address); err != nil {
+		lggr.Errorw("Contract code not available after deploy", "err", err, "symbol", symbol, "addr", mockTokenFeed.Address)
+		return common.Address{}, "", err
+	}
+
 	desc, err := mockTokenFeed.Contract.Description(&bind.CallOpts{})
 	if err != nil {
 		lggr.Errorw("Failed to get description", "err", err, "symbol", symbol)
```

### deployment/ccip/changeset/v1_6/cs_home_chain.go
```diff
@@ -25,7 +25,7 @@ import (
 	capabilities_registry "github.com/smartcontractkit/chainlink-evm/gethwrappers/keystone/generated/capabilities_registry_1_1_0"
 
 	mcmschangesets "github.com/smartcontractkit/cld-changesets/legacy/mcms/changesets"
-	proposeutils "github.com/smartcontractkit/cld-changesets/legacy/mcms/proposeutils"
+	"github.com/smartcontractkit/cld-changesets/legacy/mcms/proposeutils"
 
 	cldf_evm "github.com/smartcontractkit/chainlink-deployments-framework/chain/evm"
 	cldf "github.com/smartcontractkit/chainlink-deployments-framework/deployment"
@@ -165,6 +165,14 @@ func deployCapReg(
 		lggr.Errorw("Failed to deploy capreg", "chain", chain.String(), "err", err)
 		return nil, err
 	}
+	ctx := chain.DeployerKey.Context
+	if ctx == nil {
+		ctx = context.Background()
+	}
+	if err := shared.WaitForContractCode(ctx, chain.Client, capReg.Address); err != nil {
+		lggr.Errorw("CapabilitiesRegistry code not available after deploy", "chain", chain.String(), "addr", capReg.Address, "err", err)
+		return nil, err
+	}
 	return capReg, nil
 }
 
@@ -190,6 +198,10 @@ func deployHomeChain(
 	}
 
 	lggr.Infow("deployed/connected to capreg", "addr", capReg.Address)
+	ctx := e.GetContext()
+	if ctx == nil {
+		ctx = context.Background()
+	}
 	var ccipHomeAddr common.Address
 	if state.Chains[chain.Selector].CCIPHome != nil {
 		lggr.Infow("CCIPHome already deployed", "addr", state.Chains[chain.Selector].CCIPHome.Address().String())
@@ -211,6 +223,10 @@ func deployHomeChain(
 			lggr.Errorw("Failed to deploy CCIPHome", "chain", chain.String(), "err", err)
 			return nil, err
 		}
+		if err := shared.WaitForContractCode(ctx, chain.Client, ccipHome.Address); err != nil {
+			lggr.Errorw("CCIPHome code not available after deploy", "chain", chain.String(), "addr", ccipHome.Address, "err", err)
+			return nil, err
+		}
 		ccipHomeAddr = ccipHome.Address
 	}
 	rmnHome := state.Chains[chain.Selector].RMNHome
@@ -234,6 +250,10 @@ func deployHomeChain(
 			return nil, err
 		}
 		rmnHome = rmnHomeContract.Contract
+		if err := shared.WaitForContractCode(ctx, chain.Client, rmnHomeContract.Address); err != nil {
+			lggr.Errorw("RMNHome code not available after deploy", "chain", chain.String(), "addr", rmnHomeContract.Address, "err", err)
+			return nil, err
+		}
 	}
 
 	// considering the RMNHome is recently deployed, there is no digest to overwrite
```

### deployment/ccip/shared/wait_contract_code.go
```diff
@@ -0,0 +1,27 @@
+package shared
+
+import (
+	"context"
+	"fmt"
+	"time"
+
+	"github.com/ethereum/go-ethereum/common"
+	"github.com/sethvargo/go-retry"
+
+	cldf_evm "github.com/smartcontractkit/chainlink-deployments-framework/chain/evm"
+)
+
+// WaitForContractCode retries until bytecode is visible at addr. Geth in Docker CI can
+// return a mined receipt before eth_getCode serves the deployment on all RPC paths.
+func WaitForContractCode(ctx context.Context, client cldf_evm.OnchainClient, addr common.Address) error {
+	return retry.Do(ctx, retry.WithMaxDuration(30*time.Second, retry.WithCappedDuration(2*time.Second, retry.NewFibonacci(500*time.Millisecond))), func(ctx context.Context) error {
+		code, err := client.CodeAt(ctx, addr, nil)
+		if err != nil {
+			return retry.RetryableError(err)
+		}
+		if len(code) == 0 {
+			return retry.RetryableError(fmt.Errorf("no contract code at %s yet", addr))
+		}
+		return nil
+	})
+}
```

### integration-tests/smoke/ccip/ccip_jobspec_test.go
```diff
@@ -6,8 +6,6 @@ import (
 	"github.com/stretchr/testify/require"
 	"golang.org/x/exp/maps"
 
-	"github.com/smartcontractkit/chainlink-common/pkg/utils/tests"
-
 	jdchangesets "github.com/smartcontractkit/cld-changesets/jd/changesets"
 
 	"github.com/smartcontractkit/chainlink/deployment/ccip/changeset/testhelpers"
@@ -18,7 +16,6 @@ import (
 
 // It always runs in docker, it's not enabled to run in-memory as we are testing the actual job distributor
 func TestDeleteCCIPJobs(t *testing.T) {
-	tests.SkipFlakey(t, "https://smartcontract-it.atlassian.net/browse/CCIP-11030")
 	e, _, tenv := testsetups.NewIntegrationEnvironment(t, testhelpers.WithJobsOnly())
 	nopsView, err := view.GenerateNopsView(e.Env.Logger, e.Env.NodeIDs, e.Env.Offchain)
 	require.NoError(t, err)
@@ -53,8 +50,6 @@ func TestDeleteCCIPJobs(t *testing.T) {
 
 // It always runs in docker, it's not enabled to run in-memory as we are testing the actual job distributor
 func TestRevokeJobs(t *testing.T) {
-	tests.SkipFlakey(t, "https://smartcontract-it.atlassian.net/browse/DX-566")
-
 	e, _, _ := testsetups.NewIntegrationEnvironment(t, testhelpers.WithJobsOnly())
 	nopsView, err := view.GenerateNopsView(e.Env.Logger, e.Env.NodeIDs, e.Env.Offchain)
 	require.NoError(t, err)
```
