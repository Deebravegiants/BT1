# [?] fix(vald): panic when confirming gateway txs and tx is not finalized (#2108)

## Summary
Severity: Unknown
Chain: Axelar
Component: axelarnetwork/axelar-core
Published: 2024-02-23
Source: https://github.com/axelarnetwork/axelar-core/commit/0d6928de91bcb249f34be4ad520e275d0fc3e4eb
Type: security-commit

## Details
fix(vald): panic when confirming gateway txs and tx is not finalized (#2108)

* fix(vald): panic when confirming gateway txs and tx is not finalized

* fix log

## Patch
### vald/evm/evm.go
```diff
@@ -39,8 +39,8 @@ var (
 	TokenSentSig                    = crypto.Keccak256Hash([]byte("TokenSent(address,string,string,string,uint256)"))
 )
 
-// NotFinalized is returned when a transaction is not finalized
-var NotFinalized = goerrors.New("not finalized")
+// ErrNotFinalized is returned when a transaction is not finalized
+var ErrNotFinalized = goerrors.New("not finalized")
 
 // Mgr manages all communication with Ethereum
 type Mgr struct {
@@ -302,8 +302,8 @@ func (mgr Mgr) ProcessGatewayTxsConfirmation(event *types.ConfirmGatewayTxsStart
 			events := mgr.processGatewayTxLogs(event.Chain, event.GatewayAddress, result.Ok().Logs)
 			logger.Infof("broadcasting vote %v", events)
 			votes = append(votes, voteTypes.NewVoteRequest(mgr.proxy, pollID, types.NewVoteEvents(event.Chain, events...)))
-		case NotFinalized:
-			logger.Debug(fmt.Sprintf("transaction %s in block %s not finalized", txID.Hex(), result.Ok().BlockNumber.String()))
+		case ErrNotFinalized:
+			logger.Debug(fmt.Sprintf("transaction %s not finalized", txID.Hex()))
 			logger.Infof("broadcasting empty vote due to error: %s", result.Err().Error())
 			votes = append(votes, voteTypes.NewVoteRequest(mgr.proxy, pollID, types.NewVoteEvents(event.Chain)))
 		case ethereum.NotFound:
@@ -502,7 +502,7 @@ func (mgr Mgr) GetTxReceiptsIfFinalized(chain nexus.ChainName, txIDs []common.Ha
 		}
 
 		if !isFinalized {
-			return rs.FromErr[*geth.Receipt](NotFinalized)
+			return rs.FromErr[*geth.Receipt](ErrNotFinalized)
 		}
 
 		return rs.FromOk(receipt)
```

### vald/evm/evm_test.go
```diff
@@ -971,7 +971,7 @@ func TestMgr_GetTxReceiptsIfFinalized(t *testing.T) {
 					notFinalized := receipts[len(txHashes)/2:]
 
 					assert.True(t, slices.All(finalized, func(result results.Result[*geth.Receipt]) bool { return result.Err() == nil }))
-					assert.True(t, slices.All(notFinalized, func(result results.Result[*geth.Receipt]) bool { return result.Err() == evm.NotFinalized }))
+					assert.True(t, slices.All(notFinalized, func(result results.Result[*geth.Receipt]) bool { return result.Err() == evm.ErrNotFinalized }))
 				}),
 		).
 		Run(t, 5)
```
