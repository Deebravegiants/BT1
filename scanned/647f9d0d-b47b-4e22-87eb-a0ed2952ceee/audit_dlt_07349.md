# [?] [FAB-17525] Fix peer panic for endorser metric labels (#721)

## Summary
Severity: Unknown
Chain: Hyperledger Fabric
Component: hyperledger/fabric
Published: 2020-02-24
Source: https://github.com/hyperledger/fabric/commit/add77fa9803c768897f0bbfb9046c64345179de2
Type: security-commit

## Details
[FAB-17525] Fix peer panic for endorser metric labels (#721)

SimulationFailure endorser metrics were being emitted without the
required labels included, causing peer to panic.
The fix adds the required labels.

Signed-off-by: David Enyeart <enyeart@us.ibm.com>

## Patch
### core/endorser/endorser.go
```diff
@@ -178,6 +178,11 @@ func (e *Endorser) callChaincode(txParams *ccprovider.TransactionParams, input *
 func (e *Endorser) SimulateProposal(txParams *ccprovider.TransactionParams, chaincodeName string, chaincodeInput *pb.ChaincodeInput) (*pb.Response, []byte, *pb.ChaincodeEvent, error) {
 	logger := decorateLogger(endorserLogger, txParams)
 
+	meterLabels := []string{
+		"channel", txParams.ChannelID,
+		"chaincode", chaincodeName,
+	}
+
 	// ---3. execute the proposal and get simulation results
 	res, ccevent, err := e.callChaincode(txParams, chaincodeInput, chaincodeName)
 	if err != nil {
@@ -196,14 +201,14 @@ func (e *Endorser) SimulateProposal(txParams *ccprovider.TransactionParams, chai
 
 	simResult, err := txParams.TXSimulator.GetTxSimulationResults()
 	if err != nil {
-		e.Metrics.SimulationFailure.Add(1)
+		e.Metrics.SimulationFailure.With(meterLabels...).Add(1)
 		return nil, nil, nil, err
 	}
 
 	if simResult.PvtSimulationResults != nil {
 		if chaincodeName == "lscc" {
 			// TODO: remove once we can store collection configuration outside of LSCC
-			e.Metrics.SimulationFailure.Add(1)
+			e.Metrics.SimulationFailure.With(meterLabels...).Add(1)
 			return nil, nil, nil, errors.New("Private data is forbidden to be used in instantiate")
 		}
 		pvtDataWithConfig, err := AssemblePvtRWSet(txParams.ChannelID, simResult.PvtSimulationResults, txParams.TXSimulator, e.Support.GetDeployedCCInfoProvider())
@@ -212,12 +217,12 @@ func (e *Endorser) SimulateProposal(txParams *ccprovider.TransactionParams, chai
 		txParams.TXSimulator.Done()
 
 		if err != nil {
-			e.Metrics.SimulationFailure.Add(1)
+			e.Metrics.SimulationFailure.With(meterLabels...).Add(1)
 			return nil, nil, nil, errors.WithMessage(err, "failed to obtain collections config")
 		}
 		endorsedAt, err := e.Support.GetLedgerHeight(txParams.ChannelID)
 		if err != nil {
-			e.Metrics.SimulationFailure.Add(1)
+			e.Metrics.SimulationFailure.With(meterLabels...).Add(1)
 			return nil, nil, nil, errors.WithMessage(err, fmt.Sprintf("failed to obtain ledger height for channel '%s'", txParams.ChannelID))
 		}
 		// Add ledger height at which transaction was endorsed,
@@ -227,14 +232,14 @@ func (e *Endorser) SimulateProposal(txParams *ccprovider.TransactionParams, chai
 		// Ideally, ledger should add support in the simulator as a first class function `GetHeight()`.
 		pvtDataWithConfig.EndorsedAt = endorsedAt
 		if err := e.PrivateDataDistributor.DistributePrivateData(txParams.ChannelID, txParams.TxID, pvtDataWithConfig, endorsedAt); err != nil {
-			e.Metrics.SimulationFailure.Add(1)
+			e.Metrics.SimulationFailure.With(meterLabels...).Add(1)
 			return nil, nil, nil, err
 		}
 	}
 
 	pubSimResBytes, err := simResult.GetPubSimulationBytes()
 	if err != nil {
-		e.Metrics.SimulationFailure.Add(1)
+		e.Metrics.SimulationFailure.With(meterLabels...).Add(1)
 		return nil, nil, nil, err
 	}
 
```
