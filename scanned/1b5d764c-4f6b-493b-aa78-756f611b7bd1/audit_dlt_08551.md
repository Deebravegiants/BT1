# [?] Fix dryrun crash on rewards calculation (#2894)

## Summary
Severity: Unknown
Chain: Algorand
Component: algorand/go-algorand
Published: 2021-09-15
Source: https://github.com/algorand/go-algorand/commit/9fe1bf4851c0a1636710a269c0acaa722527a950
Type: security-commit

## Details
Fix dryrun crash on rewards calculation (#2894)

## Patch
### cmd/tealdbg/localLedger.go
```diff
@@ -285,7 +285,10 @@ func (l *localLedger) CheckDup(config.ConsensusParams, basics.Round, basics.Roun
 }
 
 func (l *localLedger) LookupWithoutRewards(rnd basics.Round, addr basics.Address) (basics.AccountData, basics.Round, error) {
-	return l.balances[addr], rnd, nil
+	ad := l.balances[addr]
+	// Clear RewardsBase since tealdbg has no idea about rewards level so the underlying calculation with reward will fail.
+	ad.RewardsBase = 0
+	return ad, rnd, nil
 }
 
 func (l *localLedger) GetCreatorForRound(rnd basics.Round, cidx basics.CreatableIndex, ctype basics.CreatableType) (basics.Address, bool, error) {
```

### daemon/algod/api/server/v2/account.go
```diff
@@ -105,7 +105,7 @@ func AccountDataToAccount(
 	amount := record.MicroAlgos
 	pendingRewards, overflowed := basics.OSubA(amount, amountWithoutPendingRewards)
 	if overflowed {
-		return generated.Account{}, errors.New("overflow on pending reward calcuation")
+		return generated.Account{}, errors.New("overflow on pending reward calculation")
 	}
 
 	return generated.Account{
```

### daemon/algod/api/server/v2/dryrun.go
```diff
@@ -273,6 +273,9 @@ func (dl *dryrunLedger) LookupWithoutRewards(rnd basics.Round, addr basics.Addre
 			return basics.AccountData{}, 0, err
 		}
 		out.MicroAlgos.Raw = acct.AmountWithoutPendingRewards
+		// Clear RewardsBase since dryrun has no idea about rewards level so the underlying calculation with reward will fail.
+		// The amount needed is known as acct.Amount but this method must return AmountWithoutPendingRewards
+		out.RewardsBase = 0
 	}
 	appi, ok := dl.accountApps[addr]
 	if ok {
```

### daemon/algod/api/server/v2/dryrun_test.go
```diff
@@ -1331,3 +1331,64 @@ func TestDryrunCost(t *testing.T) {
 		})
 	}
 }
+
+func TestDryrunBalanceWithReward(t *testing.T) {
+	partitiontest.PartitionTest(t)
+	t.Parallel()
+
+	ops, err := logic.AssembleString(`#pragma version 5
+int 0
+balance
+int 0
+>`)
+	require.NoError(t, err)
+	approval := ops.Program
+	ops, err = logic.AssembleString("int 1")
+	clst := ops.Program
+	require.NoError(t, err)
+	var appIdx basics.AppIndex = 1
+	creator := randomAddress()
+	rewardBase := uint64(10000000)
+	dr := DryrunRequest{
+		Txns: []transactions.SignedTxn{
+			{
+				Txn: transactions.Transaction{
+					Header: transactions.Header{Sender: creator},
+					Type:   protocol.ApplicationCallTx,
+					ApplicationCallTxnFields: transactions.ApplicationCallTxnFields{
+						ApplicationID: appIdx,
+					},
+				},
+			},
+		},
+		Apps: []generated.Application{
+			{
+				Id: uint64(appIdx),
+				Params: generated.ApplicationParams{
+					Creator:           creator.String(),
+					ApprovalProgram:   approval,
+					ClearStateProgram: clst,
+					LocalStateSchema:  &generated.ApplicationStateSchema{NumByteSlice: 1},
+				},
+			},
+		},
+		Accounts: []generated.Account{
+			{
+				Address:                     creator.String(),
+				Status:                      "Online",
+				Amount:                      10000000,
+				AmountWithoutPendingRewards: 10000000,
+				RewardBase:                  &rewardBase,
+			},
+		},
+	}
+	dr.ProtocolVersion = string(dryrunProtoVersion)
+
+	var response generated.DryrunResponse
+	doDryrunRequest(&dr, &response)
+	require.NoError(t, err)
+	checkAppCallPass(t, &response)
+	if t.Failed() {
+		logResponse(t, &response)
+	}
+}
```
