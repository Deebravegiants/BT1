# [?] fixes 1162; race condition between delegation record queries and withdrawal acks (#1183)

## Summary
Severity: Unknown
Chain: Quicksilver
Component: quicksilver-zone/quicksilver
Published: 2024-02-23
Source: https://github.com/quicksilver-zone/quicksilver/commit/a2adc434d9583570a70787946a80919b196f2e6e
Type: security-commit

## Details
fixes 1162; race condition between delegation record queries and withdrawal acks (#1183)

* fixes 1162; race condition between delegation record queries and withdrawal acks

* lint

## Patch
### Dockerfile
```diff
@@ -1,4 +1,4 @@
-FROM golang:1.21.7-alpine3.19 AS builder
+FROM golang:1.21.7-alpine3.18 AS builder
 RUN apk add --no-cache git musl-dev openssl-dev linux-headers ca-certificates build-base
 
 WORKDIR /src/app/
@@ -22,7 +22,7 @@ RUN --mount=type=cache,target=/root/.cache/go-build \
     LINK_STATICALLY=true make build
 
 # Add to a distroless container
-FROM alpine:3.19
+FROM alpine:3.18
 COPY --from=builder /src/app/build/quicksilverd /usr/local/bin/quicksilverd
 RUN adduser -S -h /quicksilver -D quicksilver -u 1000
 USER quicksilver
```

### scripts/registerzone.json
```diff
@@ -6,16 +6,17 @@
   "content": {
   "@type": "/quicksilver.interchainstaking.v1.RegisterZoneProposal",
   "title": "register lstest-1 zone",
-  "description": "register lstest-1 zone with multisend and lsm enabled",
+  "description": "register lstest-1 zone with lsm disabled",
   "connection_id": "connection-0",
   "base_denom": "uatom",
   "local_denom": "uqatom",
   "account_prefix": "cosmos",
   "deposits_enabled": true,
   "unbonding_enabled": true,
   "liquidity_module": false,
-  "return_to_sender": true,
-  "decimals": 6
+  "return_to_sender": false,
+  "decimals": 6,
+  "is_118": true
   },
   "authority": "quick10d07y265gmmuvt4z0w9aw880jnsr700j3xrh0p"
 }],
```

### scripts/setup.sh
```diff
@@ -477,6 +477,7 @@ fi
 ## set the 'epoch' epoch to 5m interval
 jq '.app_state.epochs.epochs = [{"identifier": "epoch","start_time": "0001-01-01T00:00:00Z","duration": "360s","current_epoch": "0","current_epoch_start_time": "0001-01-01T00:00:00Z","epoch_counting_started": false,"current_epoch_start_height": "0"},{"identifier": "day","start_time": "0001-01-01T00:00:00Z","duration": "120s","current_epoch": "0","current_epoch_start_time": "0001-01-01T00:00:00Z","epoch_counting_started": false,"current_epoch_start_height": "0"}]' ./${CHAIN_DIR}/${CHAINID_0}/config/genesis.json > ./${CHAIN_DIR}/${CHAINID_0}/config/genesis.json.new && mv ./${CHAIN_DIR}/${CHAINID_0}/config/genesis.json{.new,}
 jq '.app_state.interchainstaking.params.deposit_interval = 25' ./${CHAIN_DIR}/${CHAINID_0}/config/genesis.json > ./${CHAIN_DIR}/${CHAINID_0}/config/genesis.json.new && mv ./${CHAIN_DIR}/${CHAINID_0}/config/genesis.json{.new,}
+jq '.app_state.interchainstaking.params.unbonding_enabled = true' ./${CHAIN_DIR}/${CHAINID_0}/config/genesis.json > ./${CHAIN_DIR}/${CHAINID_0}/config/genesis.json.new && mv ./${CHAIN_DIR}/${CHAINID_0}/config/genesis.json{.new,} 
 jq '.app_state.mint.params.epoch_identifier = "epoch"' ./${CHAIN_DIR}/${CHAINID_0}/config/genesis.json > ./${CHAIN_DIR}/${CHAINID_0}/config/genesis.json.new && mv ./${CHAIN_DIR}/${CHAINID_0}/config/genesis.json{.new,}
 jq '.app_state.gov.deposit_params.min_deposit = [{"denom": "uqck", "amount": "100"}]' ./${CHAIN_DIR}/${CHAINID_0}/config/genesis.json > ./${CHAIN_DIR}/${CHAINID_0}/config/genesis.json.new && mv ./${CHAIN_DIR}/${CHAINID_0}/config/genesis.json{.new,}
 jq '.app_state.gov.deposit_params.max_deposit_period = "10s"' ./${CHAIN_DIR}/${CHAINID_0}/config/genesis.json > ./${CHAIN_DIR}/${CHAINID_0}/config/genesis.json.new && mv ./${CHAIN_DIR}/${CHAINID_0}/config/genesis.json{.new,}
```

### x/interchainstaking/keeper/callbacks.go
```diff
@@ -73,7 +73,9 @@ func (c Callbacks) RegisterCallbacks() icqtypes.QueryCallbacks {
 		AddCallback("validator", Callback(ValidatorCallback)).
 		AddCallback("rewards", Callback(RewardsCallback)).
 		AddCallback("delegations", Callback(DelegationsCallback)).
+		AddCallback("delegations_epoch", Callback(DelegationsEpochCallback)).
 		AddCallback("delegation", Callback(DelegationCallback)).
+		AddCallback("delegation_epoch", Callback(DelegationEpochCallback)).
 		AddCallback("distributerewards", Callback(DistributeRewardsFromWithdrawAccount)).
 		AddCallback("depositinterval", Callback(DepositIntervalCallback)).
 		AddCallback("deposittx", Callback(DepositTxCallback)).
@@ -124,17 +126,25 @@ func RewardsCallback(k *Keeper, ctx sdk.Context, args []byte, query icqtypes.Que
 
 	// decrement waitgroup as we have received back the query
 	// (initially incremented in AfterEpochEnd)
-	err = zone.DecrementWithdrawalWaitgroup(k.Logger(ctx), 1, "rewards callback")
-	if err != nil {
-		return err
+	if err = zone.DecrementWithdrawalWaitgroup(k.Logger(ctx), 1, "rewards callback"); err != nil {
+		// given that there _could_ be a backlog of message, we don't want to bail here, else they will remain undeliverable.
+		k.Logger(ctx).Error(err.Error())
 	}
 
 	k.Logger(ctx).Debug("QueryDelegationRewards callback", "wg", zone.GetWithdrawalWaitgroup(), "delegatorAddress", rewardsQuery.DelegatorAddress, "zone", query.ChainId)
 
 	return k.WithdrawDelegationRewardsForResponse(ctx, &zone, rewardsQuery.DelegatorAddress, args)
 }
 
+func DelegationsEpochCallback(k *Keeper, ctx sdk.Context, args []byte, query icqtypes.Query) error {
+	return delegationsCallback(k, ctx, args, query, true)
+}
+
 func DelegationsCallback(k *Keeper, ctx sdk.Context, args []byte, query icqtypes.Query) error {
+	return delegationsCallback(k, ctx, args, query, false)
+}
+
+func delegationsCallback(k *Keeper, ctx sdk.Context, args []byte, query icqtypes.Query, isEpoch bool) error {
 	zone, found := k.GetZone(ctx, query.GetChainId())
 	if !found {
 		return fmt.Errorf("no registered zone for chain id: %s", query.GetChainId())
@@ -152,10 +162,18 @@ func DelegationsCallback(k *Keeper, ctx sdk.Context, args []byte, query icqtypes
 
 	k.Logger(ctx).Debug("Delegations callback triggered", "chain", zone.ChainId)
 
-	return k.UpdateDelegationRecordsForAddress(ctx, zone, delegationQuery.DelegatorAddr, args)
+	return k.UpdateDelegationRecordsForAddress(ctx, zone, delegationQuery.DelegatorAddr, args, isEpoch)
+}
+
+func DelegationEpochCallback(k *Keeper, ctx sdk.Context, args []byte, query icqtypes.Query) error {
+	return delegationCallback(k, ctx, args, query, true)
 }
 
 func DelegationCallback(k *Keeper, ctx sdk.Context, args []byte, query icqtypes.Query) error {
+	return delegationCallback(k, ctx, args, query, false)
+}
+
+func delegationCallback(k *Keeper, ctx sdk.Context, args []byte, query icqtypes.Query, isEpoch bool) error {
 	zone, found := k.GetZone(ctx, query.GetChainId())
 	if !found {
 		return fmt.Errorf("no registered zone for chain id: %s", query.GetChainId())
@@ -204,7 +222,7 @@ func DelegationCallback(k *Keeper, ctx sdk.Context, args []byte, query icqtypes.
 		return err
 	}
 
-	return k.UpdateDelegationRecordForAddress(ctx, delegation.DelegatorAddress, delegation.ValidatorAddress, sdk.NewCoin(zone.BaseDenom, val.SharesToTokens(delegation.Shares)), &zone, true)
+	return k.UpdateDelegationRecordForAddress(ctx, delegation.DelegatorAddress, delegation.ValidatorAddress, sdk.NewCoin(zone.BaseDenom, val.SharesToTokens(delegation.Shares)), &zone, true, isEpoch)
 }
 
 func PerfBalanceCallback(k *Keeper, ctx sdk.Context, response []byte, query icqtypes.Query) error {
@@ -622,9 +640,9 @@ func DelegationAccountBalanceCallback(k *Keeper, ctx sdk.Context, args []byte, q
 	}
 
 	k.Logger(ctx).Info("Received balance response for denom", "denom", coin.Denom)
-	err = zone.DecrementWithdrawalWaitgroup(k.Logger(ctx), 1, "delegationaccountbalance callback")
-	if err != nil {
-		return err
+	if err = zone.DecrementWithdrawalWaitgroup(k.Logger(ctx), 1, "delegationaccountbalance callback"); err != nil {
+		// given that there _could_ be a backlog of message, we don't want to bail here, else they will remain undeliverable.
+		k.Logger(ctx).Error(err.Error())
 	}
 
 	// set the zone amount.
@@ -645,6 +663,12 @@ func DelegationAccountBalanceCallback(k *Keeper, ctx sdk.Context, args []byte, q
 	// if token is not valid for staking, then send to withdrawal account.
 	if valid, _ := zone.ValidateCoinsForZone(sdk.NewCoins(coin), k.GetValidatorAddressesAsMap(ctx, zone.ChainId)); !valid {
 		k.Logger(ctx).Info("token is not a valid staking token, so sending to withdrawal account for disbursal", "chain", zone.ChainId, "assets", coin)
+		if zone.GetWithdrawalWaitgroup() == 0 {
+			k.Logger(ctx).Info("triggering redemption rate calc in lieu of delegation flush")
+			if err := k.TriggerRedemptionRate(ctx, &zone); err != nil {
+				return err
+			}
+		}
 		return k.SendToWithdrawal(ctx, &zone, zone.DelegationAddress, sdk.NewCoins(coin))
 	}
 
@@ -660,7 +684,8 @@ func DelegationAccountBalancesCallback(k *Keeper, ctx sdk.Context, args []byte,
 	k.cdc.MustUnmarshal(args, &result)
 
 	if err := zone.DecrementWithdrawalWaitgroup(k.Logger(ctx), 1, "delegationaccountbalances callback"); err != nil {
-		return err
+		// given that there _could_ be a backlog of message, we don't want to bail here, else they will remain undeliverable.
+		k.Logger(ctx).Error(err.Error())
 	}
 
 	addressBytes, err := addressutils.AccAddressFromBech32(zone.DelegationAddress.Address, zone.AccountPrefix)
```

### x/interchainstaking/keeper/callbacks_test.go
```diff
@@ -2649,7 +2649,7 @@ func (suite *KeeperTestSuite) TestDelegationAccountBalancesCallbackNoWg() {
 			suite.Require().NoError(err)
 
 			err = keeper.DelegationAccountBalancesCallback(app.InterchainstakingKeeper, ctx, respbz, icqtypes.Query{ChainId: suite.chainB.ChainID, Request: reqbz})
-			suite.Require().Error(err)
+			suite.Require().NoError(err) // was previously error but we no longer fail here, just exit with nil.
 		})
 	}
 }
```

### x/interchainstaking/keeper/delegation.go
```diff
@@ -329,7 +329,8 @@ func (k *Keeper) FlushOutstandingDelegations(ctx sdk.Context, zone *types.Zone,
 		k.Logger(ctx).Info("delegate account balance negative, or nothing to flush, setting outdated receipts")
 		k.SetReceiptsCompleted(ctx, zone.ChainId, exclusionTime, ctx.BlockTime(), delAddrBalance.Denom)
 		if zone.GetWithdrawalWaitgroup() == 0 {
-			k.Logger(ctx).Info("triggering redemption rate calc in lieu of delegation flush")
+			// we won't be sending any messages when we exit here; so if WG==0, then trigger RR update
+			k.Logger(ctx).Info("triggering redemption rate calc in lieu of delegation flush (non-positive coins)")
 			if err := k.TriggerRedemptionRate(ctx, zone); err != nil {
 				return err
 			}
@@ -352,6 +353,15 @@ func (k *Keeper) FlushOutstandingDelegations(ctx sdk.Context, zone *types.Zone,
 	if err = zone.IncrementWithdrawalWaitgroup(k.Logger(ctx), uint32(numMsgs), "sending flush messages"); err != nil {
 		return err
 	}
+
+	// if we didn't send any messages (thus no acks will happen), and WG==0, then trigger RR update
+	if numMsgs == 0 && zone.GetWithdrawalWaitgroup() == 0 {
+		k.Logger(ctx).Info("triggering redemption rate calc in lieu of delegation flush (no messages to send)")
+		if err := k.TriggerRedemptionRate(ctx, zone); err != nil {
+			return err
+		}
+	}
+
 	k.SetZone(ctx, zone)
 	return nil
 }
```

### x/interchainstaking/keeper/delegation_test.go
```diff
@@ -217,7 +217,7 @@ func (suite *KeeperTestSuite) TestUpdateDelegation() {
 			}
 
 			for _, update := range tt.updates {
-				err := qApp.InterchainstakingKeeper.UpdateDelegationRecordForAddress(ctx, update.delegation.DelegationAddress, update.delegation.ValidatorAddress, update.delegation.Amount, &zone, update.absolute)
+				err := qApp.InterchainstakingKeeper.UpdateDelegationRecordForAddress(ctx, update.delegation.DelegationAddress, update.delegation.ValidatorAddress, update.delegation.Amount, &zone, update.absolute, false)
 				suite.NoError(err)
 			}
 
```

### x/interchainstaking/keeper/hooks.go
```diff
@@ -101,6 +101,10 @@ func (k *Keeper) AfterEpochEnd(ctx sdk.Context, epochIdentifier string, epochNum
 			return false
 		})
 
+		if zone.GetWithdrawalWaitgroup() > 0 {
+			zone.SetWithdrawalWaitgroup(k.Logger(ctx), 0, "epoch waitgroup was unexpected > 0")
+		}
+
 		if err := k.HandleQueuedUnbondings(ctx, zone, epochNumber); err != nil {
 			// we can and need not panic here; logging the error is sufficient.
 			// an error here is not expected, but also not terminal.
@@ -130,10 +134,6 @@ func (k *Keeper) AfterEpochEnd(ctx sdk.Context, epochIdentifier string, epochNum
 			)
 		}
 
-		if zone.GetWithdrawalWaitgroup() > 0 {
-			zone.SetWithdrawalWaitgroup(k.Logger(ctx), 0, "epoch waitgroup was unexpected > 0")
-		}
-
 		// OnChanOpenAck calls SetWithdrawalAddress (see ibc_module.go)
 		k.Logger(ctx).Info(
 			"withdrawing rewards",
@@ -154,10 +154,12 @@ func (k *Keeper) AfterEpochEnd(ctx sdk.Context, epochIdentifier string, epochNum
 			bz,
 			sdk.NewInt(-1),
 			types.ModuleName,
-			"delegations",
+			"delegations_epoch",
 			0,
 		)
 
+		_ = zone.IncrementWithdrawalWaitgroup(k.Logger(ctx), 1, "delegations trigger")
+
 		balancesQuery := banktypes.QueryAllBalancesRequest{Address: zone.DelegationAddress.Address}
 		bz = k.cdc.MustMarshal(&balancesQuery)
 		k.ICQKeeper.MakeRequest(
```

### x/interchainstaking/keeper/ibc_packet_handlers.go
```diff
@@ -369,6 +369,10 @@ func (k *Keeper) HandleCompleteSend(ctx sdk.Context, msg sdk.Msg, memo string) e
 		k.Logger(ctx).Info("delegate account send tokens; handling withdrawal", "amount", sMsg.Amount, "memo", memo)
 		return k.HandleWithdrawForUser(ctx, zone, sMsg, memo)
 
+	case zone.IsDepositAddress(sMsg.FromAddress) && memo == "refund":
+		k.Logger(ctx).Info("unable to process deposit, returning funds to sender", "recipient", sMsg.ToAddress, "amount", sMsg.Amount, "memo", memo)
+		return nil
+
 	default:
 		err = fmt.Errorf("unexpected completed send (2) from %s to %s (amount: %s)", sMsg.FromAddress, sMsg.ToAddress, sMsg.Amount)
 		k.Logger(ctx).Error(err.Error())
@@ -705,6 +709,11 @@ func (k *Keeper) HandleUndelegate(ctx sdk.Context, msg sdk.Msg, completion time.
 	if !found {
 		return fmt.Errorf("zone for delegate account %s not found", undelegateMsg.DelegatorAddress)
 	}
+
+	if err := zone.DecrementWithdrawalWaitgroup(k.Logger(ctx), 1, "unbonding message ack"); err != nil {
+		// given that there _could_ be a backlog of message, we don't want to bail here, else they will remain undeliverable.
+		k.Logger(ctx).Error(err.Error())
+	}
 	ubr, found := k.GetUnbondingRecord(ctx, zone.ChainId, undelegateMsg.ValidatorAddress, epochNumber)
 	if !found {
 		return fmt.Errorf("unbonding record for %s not found for epoch %d", undelegateMsg.ValidatorAddress, epochNumber)
@@ -747,10 +756,15 @@ func (k *Keeper) HandleUndelegate(ctx sdk.Context, msg sdk.Msg, completion time.
 		data,
 		sdk.NewInt(-1),
 		types.ModuleName,
-		"delegation",
+		"delegation_epoch",
 		0,
 	)
 
+	if err = zone.IncrementWithdrawalWaitgroup(k.Logger(ctx), 1, "unbonding message ack emit delegation_epoch query"); err != nil {
+		return err
+	}
+	k.SetZone(ctx, zone)
+
 	return nil
 }
 
@@ -937,7 +951,7 @@ func (k *Keeper) HandleRedeemTokens(ctx sdk.Context, msg sdk.Msg, amount sdk.Coi
 		receipt.Completed = &t
 		k.SetReceipt(ctx, receipt)
 	}
-	return k.UpdateDelegationRecordForAddress(ctx, redeemMsg.DelegatorAddress, validatorAddress, amount, zone, false)
+	return k.UpdateDelegationRecordForAddress(ctx, redeemMsg.DelegatorAddress, validatorAddress, amount, zone, false, false)
 }
 
 func (k *Keeper) HandleFailedRedeemTokens(ctx sdk.Context, msg sdk.Msg, memo string) error {
@@ -961,7 +975,9 @@ func (k *Keeper) HandleFailedRedeemTokens(ctx sdk.Context, msg sdk.Msg, memo str
 	case strings.HasPrefix(memo, "batch"):
 		k.Logger(ctx).Error("batch token redemption failed", "memo", memo, "tx", redeemMsg)
 		if err := zone.DecrementWithdrawalWaitgroup(k.Logger(ctx), uint32(1), "batch token redemption failure ack"); err != nil {
-			return err
+			k.Logger(ctx).Error(err.Error())
+			return nil
+			// return nil here so we don't reject the incoming tx, but log the error and don't trigger RR update for repeated zero.
 		}
 		k.Logger(ctx).Info("Decremented waitgroup after failed batch token redemption", "wg", zone.GetWithdrawalWaitgroup())
 		k.SetZone(ctx, zone)
@@ -1006,7 +1022,9 @@ func (k *Keeper) HandleDelegate(ctx sdk.Context, msg sdk.Msg, memo string) error
 		k.SetReceiptsCompleted(ctx, zone.ChainId, time.Unix(exclusionTimestampUnix, 0), ctx.BlockTime(), delegateMsg.Amount.Denom)
 		zone.DelegationAddress.Balance = zone.DelegationAddress.Balance.Sub(delegateMsg.Amount)
 		if err := zone.DecrementWithdrawalWaitgroup(k.Logger(ctx), uint32(1), "batch/reward delegation success ack"); err != nil {
-			return err
+			k.Logger(ctx).Error(err.Error())
+			return nil
+			// return nil here so we don't reject the incoming tx, but log the error and don't trigger RR update for repeated zero.
 		}
 		k.SetZone(ctx, zone)
 		if zone.GetWithdrawalWaitgroup() == 0 {
@@ -1026,7 +1044,7 @@ func (k *Keeper) HandleDelegate(ctx sdk.Context, msg sdk.Msg, memo string) error
 
 	}
 
-	return k.UpdateDelegationRecordForAddress(ctx, delegateMsg.DelegatorAddress, delegateMsg.ValidatorAddress, delegateMsg.Amount, zone, false)
+	return k.UpdateDelegationRecordForAddress(ctx, delegateMsg.DelegatorAddress, delegateMsg.ValidatorAddress, delegateMsg.Amount, zone, false, false)
 }
 
 func (k *Keeper) HandleFailedDelegate(ctx sdk.Context, msg sdk.Msg, memo string) error {
@@ -1050,7 +1068,9 @@ func (k *Keeper) HandleFailedDelegate(ctx sdk.Context, msg sdk.Msg, memo string)
 	case strings.HasPrefix(memo, "batch"):
 		k.Logger(ctx).Error("batch delegation failed", "memo", memo, "tx", delegateMsg)
 		if err := zone.DecrementWithdrawalWaitgroup(k.Logger(ctx), 1, "batch delegation failed ack"); err != nil {
-			return err
+			k.Logger(ctx).Error(err.Error())
+			return nil
+			// return nil here so we don't reject the incoming tx, but log the error and don't trigger RR update for repeated zero.
 		}
 		k.SetZone(ctx, zone)
 		if zone.GetWithdrawalWaitgroup() == 0 {
@@ -1117,13 +1137,16 @@ func (k *Keeper) GetValidatorForToken(ctx sdk.Context, amount sdk.Coin) (string,
 	return "", fmt.Errorf("unable to find validator for token %s", amount.Denom)
 }
 
-func (k *Keeper) UpdateDelegationRecordsForAddress(ctx sdk.Context, zone types.Zone, delegatorAddress string, args []byte) error {
+// UpdateDelegationRecordsForAddress accepts a QueryDelegatorDelegationsResponse and for new, or changed delegation records will
+// trigger an ICQ request for that record. If this was triggered by an epoch, the withdrawal waitgroup should be decremented once,
+// (for the incoming message) and incremented for each outgoing message.
+func (k *Keeper) UpdateDelegationRecordsForAddress(ctx sdk.Context, zone types.Zone, delegatorAddress string, args []byte, isEpoch bool) error {
 	var response stakingtypes.QueryDelegatorDelegationsResponse
 	err := k.cdc.Unmarshal(args, &response)
 	if err != nil {
 		return err
 	}
-	k.Logger(ctx).Info("Delegation query response", "response", response)
+	k.Logger(ctx).Info("Delegation query response", "isEpoch", isEpoch, "response", response)
 	_, delAddr, err := bech32.DecodeAndConvert(delegatorAddress)
 	if err != nil {
 		return err
@@ -1134,6 +1157,16 @@ func (k *Keeper) UpdateDelegationRecordsForAddress(ctx sdk.Context, zone types.Z
 	for _, del := range delegatorDelegations {
 		delMap[del.ValidatorAddress] = del
 	}
+
+	cb := "delegation"
+	if isEpoch {
+		if err := zone.DecrementWithdrawalWaitgroup(k.Logger(ctx), 1, "delegations_epoch callback succeeded"); err != nil {
+			k.Logger(ctx).Error(err.Error())
+			// don't return here, catch and squash err.
+		}
+		cb = "delegation_epoch"
+	}
+
 	for _, delegationRecord := range response.DelegationResponses {
 
 		_, valAddr, err := bech32.DecodeAndConvert(delegationRecord.Delegation.ValidatorAddress)
@@ -1154,10 +1187,15 @@ func (k *Keeper) UpdateDelegationRecordsForAddress(ctx sdk.Context, zone types.Z
 				data,
 				sdk.NewInt(-1),
 				types.ModuleName,
-				"delegation",
+				cb,
 				0,
 			)
-			// zone.DelegationAddress.IncrementBalanceWaitgroup() // does this get decremented?
+			if isEpoch {
+				err = zone.IncrementWithdrawalWaitgroup(k.Logger(ctx), 1, fmt.Sprintf("delegation callback emit %s query", cb))
+				if err != nil {
+					return err
+				}
+			}
 		}
 
 		if ok {
@@ -1182,9 +1220,19 @@ func (k *Keeper) UpdateDelegationRecordsForAddress(ctx sdk.Context, zone types.Z
 			data,
 			sdk.NewInt(-1),
 			types.ModuleName,
-			"delegation",
+			cb,
 			0,
 		)
+		if isEpoch {
+			err = zone.IncrementWithdrawalWaitgroup(k.Logger(ctx), 1, fmt.Sprintf("delegations callback emit %s query", cb))
+			if err != nil {
+				return err
+			}
+		}
+	}
+
+	if isEpoch {
+		k.SetZone(ctx, &zone)
 	}
 
 	return nil
@@ -1197,6 +1245,7 @@ func (k *Keeper) UpdateDelegationRecordForAddress(
 	amount sdk.Coin,
 	zone *types.Zone,
 	absolute bool,
+	isEpoch bool,
 ) error {
 	delegation, found := k.GetDelegation(ctx, zone.ChainId, delegatorAddress, validatorAddress)
 
@@ -1220,6 +1269,25 @@ func (k *Keeper) UpdateDelegationRecordForAddress(
 	if err != nil {
 		return err
 	}
+
+	if isEpoch {
+		err = zone.DecrementWithdrawalWaitgroup(k.Logger(ctx), 1, "delegation_epoch success")
+		if err != nil {
+			k.Logger(ctx).Error(err.Error())
+			// return nil here as to not fail the ack, but don't trigger RR multiple times.
+			return nil
+		}
+
+		k.SetZone(ctx, zone)
+
+		if zone.GetWithdrawalWaitgroup() == 0 {
+			k.Logger(ctx).Info("Triggering redemption rate upgrade after delegation updates")
+			err = k.TriggerRedemptionRate(ctx, zone)
+			if err != nil {
+				return err
+			}
+		}
+	}
 	return nil
 }
 
@@ -1244,7 +1312,9 @@ func (k *Keeper) HandleWithdrawRewards(ctx sdk.Context, msg sdk.Msg) error {
 	// performance only.
 	if withdrawalMsg.DelegatorAddress != zone.PerformanceAddress.Address {
 		if err := zone.DecrementWithdrawalWaitgroup(k.Logger(ctx), 1, "handle withdraw rewards"); err != nil {
-			return err
+			k.Logger(ctx).Error(err.Error())
+			return nil
+			// return nil here so we don't reject the incoming tx, but log the error and don't trigger RR update for repeated zero.
 		}
 		if err != nil {
 			return err
```

### x/interchainstaking/keeper/ibc_packet_handlers_test.go
```diff
@@ -824,7 +824,7 @@ func (suite *KeeperTestSuite) TestHandleWithdrawRewards() {
 				}
 			},
 			triggered: false,
-			err:       true,
+			err:       false, // was true but we don't fail on this case now in case historic messages needs to be delivered after wg zeroed.
 		},
 		{
 			name: "valid case with balances != 0",
@@ -4603,30 +4603,6 @@ func (suite *KeeperTestSuite) TestHandleFailedDelegate_Batch_OK() {
 	suite.Equal(uint32(99), zone.GetWithdrawalWaitgroup())
 }
 
-func (suite *KeeperTestSuite) TestHandleFailedDelegate_Batch_BadWg() {
-	suite.SetupTest()
-	suite.setupTestZones()
-
-	app := suite.GetQuicksilverApp(suite.chainA)
-	ctx := suite.chainA.GetContext()
-
-	zone, found := app.InterchainstakingKeeper.GetZone(ctx, suite.chainB.ChainID)
-	suite.True(found)
-
-	zone.SetWithdrawalWaitgroup(app.Logger(), 0, "init")
-	app.InterchainstakingKeeper.SetZone(ctx, &zone)
-
-	vals := app.InterchainstakingKeeper.GetValidatorAddresses(ctx, suite.chainB.ChainID)
-	msg := stakingtypes.MsgDelegate{DelegatorAddress: zone.DelegationAddress.Address, ValidatorAddress: vals[0], Amount: sdk.NewCoin("uatom", sdk.NewInt(100))}
-	var msgMsg sdk.Msg = &msg
-	err := app.InterchainstakingKeeper.HandleFailedDelegate(ctx, msgMsg, "batch/12345678")
-	suite.Error(err)
-
-	zone, found = app.InterchainstakingKeeper.GetZone(ctx, suite.chainB.ChainID)
-	suite.True(found)
-	suite.Equal(uint32(0), zone.GetWithdrawalWaitgroup())
-}
-
 func (suite *KeeperTestSuite) TestHandleFailedDelegate_PerfAddress_OK() {
 	suite.SetupTest()
 	suite.setupTestZones()
```

### x/interchainstaking/keeper/receipt.go
```diff
@@ -197,7 +197,7 @@ func (k *Keeper) MintAndSendQAsset(ctx sdk.Context, sender sdk.AccAddress, sende
 		if !found {
 			// if not found, skip minting and refund assets
 			msg := &banktypes.MsgSend{FromAddress: zone.DepositAddress.GetAddress(), ToAddress: senderAddress, Amount: assets}
-			return k.SubmitTx(ctx, []sdk.Msg{msg}, zone.DepositAddress, "", zone.MessagesPerTx)
+			return k.SubmitTx(ctx, []sdk.Msg{msg}, zone.DepositAddress, "refund", zone.MessagesPerTx)
 		}
 		// do not set, since mapped address already exists
 		setMappedAddress = false
@@ -212,6 +212,7 @@ func (k *Keeper) MintAndSendQAsset(ctx sdk.Context, sender sdk.AccAddress, sende
 	switch {
 	case zone.ReturnToSender || memoRTS:
 		err = k.SendTokenIBC(ctx, k.AccountKeeper.GetModuleAddress(types.ModuleName), senderAddress, zone, qAssets[0])
+		k.Logger(ctx).Info("Transferred qAssets via rts", "address", senderAddress, "assets", qAssets)
 
 	case mappedAddress != nil && !zone.Is_118:
 		// set mapped account
@@ -221,17 +222,17 @@ func (k *Keeper) MintAndSendQAsset(ctx sdk.Context, sender sdk.AccAddress, sende
 
 		// set send to mapped account
 		err = k.BankKeeper.SendCoinsFromModuleToAccount(ctx, types.ModuleName, mappedAddress, qAssets)
+		k.Logger(ctx).Info("Transferred qAssets to mapped account", "address", mappedAddress, "assets", qAssets)
 	default:
 		err = k.BankKeeper.SendCoinsFromModuleToAccount(ctx, types.ModuleName, sender, qAssets)
+		k.Logger(ctx).Info("Transferred qAssets to sender", "address", sender, "assets", qAssets)
 
 	}
 
 	if err != nil {
 		return fmt.Errorf("unable to transfer coins: %w", err)
 	}
 
-	k.Logger(ctx).Info("Transferred qAssets to sender", "assets", qAssets, "sender", sender)
-
 	ctx.EventManager().EmitEvent(
 		sdk.NewEvent(
 			minttypes.EventTypeMint,
```

### x/interchainstaking/keeper/redemptions.go
```diff
@@ -250,6 +250,11 @@ func (k *Keeper) HandleQueuedUnbondings(ctx sdk.Context, zone *types.Zone, epoch
 		}
 	}
 
+	if err = zone.IncrementWithdrawalWaitgroup(k.Logger(ctx), uint32(len(msgs)), "trigger unbonding messages"); err != nil {
+		return err
+	}
+	k.SetZone(ctx, zone)
+
 	return nil
 }
 
```
