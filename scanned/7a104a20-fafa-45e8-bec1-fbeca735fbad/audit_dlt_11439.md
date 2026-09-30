# [?] fix panic in load test (#1069)

## Summary
Severity: Unknown
Chain: Bridge
Component: smartcontractkit/ccip
Published: 2024-06-21
Source: https://github.com/smartcontractkit/ccip/commit/acb2d60d10f20d7ab2664108de7bedb2b6923d42
Type: security-commit

## Details
fix panic in load test (#1069)

## Patch
### integration-tests/ccip-tests/load/ccip_loadgen.go
```diff
@@ -286,23 +286,29 @@ func (c *CCIPE2ELoad) Call(_ *wasp.Generator) *wasp.Response {
 	lggr.Info().Str("tx", sendTx.Hash().Hex()).Msg("waiting for tx to be mined")
 	ctx, cancel := context.WithTimeout(context.Background(), sourceCCIP.Common.ChainClient.GetNetworkConfig().Timeout.Duration)
 	defer cancel()
-	rcpt, err1 := bind.WaitMined(ctx, sourceCCIP.Common.ChainClient.DeployBackend(), sendTx)
-	if err1 == nil {
-		hdr, err1 := c.Lane.Source.Common.ChainClient.HeaderByNumber(context.Background(), rcpt.BlockNumber)
-		if err1 == nil {
-			txConfirmationTime = hdr.Timestamp
-		}
+	rcpt, err := bind.WaitMined(ctx, sourceCCIP.Common.ChainClient.DeployBackend(), sendTx)
+	if err != nil {
+		res.Error = fmt.Sprintf("ccip-send request tx not mined, err=%s", err.Error())
+		res.Failed = true
+		res.Data = stats.StatusByPhase
+		return res
 	}
-	lggr = lggr.With().Str("Msg Tx", sendTx.Hash().String()).Logger()
-	var gasUsed uint64
-	if rcpt != nil {
-		gasUsed = rcpt.GasUsed
+	if rcpt == nil {
+		res.Error = "ccip-send request tx not mined, receipt is nil"
+		res.Failed = true
+		res.Data = stats.StatusByPhase
+		return res
 	}
+	hdr, err := c.Lane.Source.Common.ChainClient.HeaderByNumber(context.Background(), rcpt.BlockNumber)
+	if err == nil && hdr != nil {
+		txConfirmationTime = hdr.Timestamp
+	}
+	lggr = lggr.With().Str("Msg Tx", sendTx.Hash().String()).Logger()
 	if rcpt.Status != types.ReceiptStatusSuccessful {
 		stats.UpdateState(&lggr, 0, testreporters.TX, txConfirmationTime.Sub(startTime), testreporters.Failure,
 			testreporters.TransactionStats{
 				Fee:                fee.String(),
-				GasUsed:            gasUsed,
+				GasUsed:            rcpt.GasUsed,
 				TxHash:             sendTx.Hash().Hex(),
 				NoOfTokensSent:     len(msg.TokenAmounts),
 				MessageBytesLength: int64(len(msg.Data)),
@@ -319,7 +325,7 @@ func (c *CCIPE2ELoad) Call(_ *wasp.Generator) *wasp.Response {
 	stats.UpdateState(&lggr, 0, testreporters.TX, txConfirmationTime.Sub(startTime), testreporters.Success,
 		testreporters.TransactionStats{
 			Fee:                fee.String(),
-			GasUsed:            gasUsed,
+			GasUsed:            rcpt.GasUsed,
 			TxHash:             sendTx.Hash().Hex(),
 			NoOfTokensSent:     len(msg.TokenAmounts),
 			MessageBytesLength: int64(len(msg.Data)),
```
