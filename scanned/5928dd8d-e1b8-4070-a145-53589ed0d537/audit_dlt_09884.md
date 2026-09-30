# [?] [api] fix estimateGas panic for StakeMigrate (#4320)

## Summary
Severity: Unknown
Chain: IoTeX
Component: iotexproject/iotex-core
Published: 2024-07-02
Source: https://github.com/iotexproject/iotex-core/commit/05a44051bedc2f1e85b3f742f2846a4aa42d8c05
Type: security-commit

## Details
[api] fix estimateGas panic for StakeMigrate (#4320)

Co-authored-by: dustinxie <dahuaxie@gmail.com>

## Patch
### api/coreservice.go
```diff
@@ -1500,6 +1500,21 @@ func (core *coreService) EstimateGasForNonExecution(actType action.Action) (uint
 
 // EstimateMigrateStakeGasConsumption estimates gas consumption for migrate stake action
 func (core *coreService) EstimateMigrateStakeGasConsumption(ctx context.Context, ms *action.MigrateStake, caller address.Address) (uint64, error) {
+	g := core.bc.Genesis()
+	header, err := core.bc.BlockHeaderByHeight(core.bc.TipHeight())
+	if err != nil {
+		return 0, err
+	}
+	zeroAddr, err := address.FromString(address.ZeroAddress)
+	if err != nil {
+		return 0, err
+	}
+	ctx = protocol.WithBlockCtx(ctx, protocol.BlockCtx{
+		BlockHeight:    header.Height() + 1,
+		BlockTimeStamp: header.Timestamp().Add(g.BlockInterval),
+		GasLimit:       g.BlockGasLimitByHeight(header.Height() + 1),
+		Producer:       zeroAddr,
+	})
 	exec, err := staking.FindProtocol(core.registry).ConstructExecution(ctx, ms, core.sf)
 	if err != nil {
 		return 0, err
```

### e2etest/native_staking_test.go
```diff
@@ -949,6 +949,21 @@ func TestCandidateTransferOwnership(t *testing.T) {
 					&accountExpect{identityset.Address(stakerID), "99989899999999999996125955", test.nonceMgr[identityset.Address(stakerID).String()]},
 				},
 			},
+			{
+				name: "estimateGas",
+				act:  &actionWithTime{mustNoErr(action.SignedCreateStake(test.nonceMgr.pop(identityset.Address(stakerID).String()), "cand1", stakeAmount.String(), stakeDurationDays, true, nil, gasLimit, gasPrice, identityset.PrivateKey(stakerID), action.WithChainID(chainID))), stakeTime},
+				expect: []actionExpect{&functionExpect{func(test *e2etest, act *action.SealedEnvelope, receipt *action.Receipt, err error) {
+					ms, err := action.NewMigrateStake(0, 3, gasLimit, gasPrice)
+					require.NoError(err)
+					resp, err := test.api.EstimateActionGasConsumption(context.Background(), &iotexapi.EstimateActionGasConsumptionRequest{
+						Action:        &iotexapi.EstimateActionGasConsumptionRequest_StakeMigrate{StakeMigrate: ms.Proto()},
+						CallerAddress: identityset.Address(3).String(),
+						GasPrice:      gasPrice.String(),
+					})
+					require.NoError(err)
+					require.Equal(uint64(194934), resp.Gas)
+				}}},
+			},
 		})
 	})
 	t.Run("new endorsement", func(t *testing.T) {
```
