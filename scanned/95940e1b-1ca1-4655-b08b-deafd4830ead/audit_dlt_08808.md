# [?] Bug fix uint64 overflow. Add showalways option

## Summary
Severity: Unknown
Chain: Polygon zkEVM
Component: 0xPolygon/zkevm-node
Published: 2023-12-20
Source: https://github.com/0xPolygon/zkevm-node/commit/5fd6929912d56adeec9df961fec498fd159dc34d
Type: security-commit

## Details
Bug fix uint64 overflow. Add showalways option

## Patch
### tools/egp/main.go
```diff
@@ -28,6 +28,7 @@ var (
 	showErrors bool
 	showLosses bool
 	showDetail bool
+	showAlways bool
 )
 
 const (
@@ -51,44 +52,44 @@ type egpLogRecord struct {
 	l2BlockNum        uint64
 	l2BlockReceived   time.Time
 	encoded           string
-	missingLogInfo    bool   // Flag if egp_log field is empty
-	LogError          string `json:"Error"`
-	LogEnabled        bool   `json:"Enabled"`
-	LogL1GasPrice     uint64 `json:"L1GasPrice"`     // L1 gas price
-	LogBalanceOC      bool   `json:"BalanceOC"`      // uses opcode to query balance
-	LogGasPriceOC     bool   `json:"GasPriceOC"`     // uses opcode to query gas price
-	LogGasUsedFirst   uint64 `json:"GasUsedFirst"`   // execute estimate gas
-	LogGasUsedSecond  uint64 `json:"GasUsedSecond"`  // after execute gas
-	LogL2GasPrice     uint64 `json:"L2GasPrice"`     // L2 gas price = LogL1GasPrice * l2GasPriceSugFactor
-	LogGasPrice       uint64 `json:"GasPrice"`       // user gas price (signed) = L2 gas price
-	LogValueFirst     uint64 `json:"ValueFirst"`     // effective gas price using LogGasUsedFirst (EGP)
-	LogValueSecond    uint64 `json:"ValueSecond"`    // effective gas price using LogGasUsedSecond (NEGP)
-	LogValueFinal     uint64 `json:"ValueFinal"`     // final gas price
-	LogReprocess      bool   `json:"Reprocess"`      // reprocessed (executed 2 times)
-	LogPercentage     uint64 `json:"Percentage"`     // user gas/final gas, coded percentage (0:not used, 1..255)
-	LogMaxDeviation   uint64 `json:"MaxDeviation"`   // max allowed deviation = LogValueFirst * finalDeviationPct
-	LogFinalDeviation uint64 `json:"FinalDeviation"` // final gas deviation = abs(LogValueSecond - LogValueFirst)
+	missingLogInfo    bool    // Flag if egp_log field is empty
+	LogError          string  `json:"Error"`
+	LogEnabled        bool    `json:"Enabled"`
+	LogL1GasPrice     float64 `json:"L1GasPrice"`     // L1 gas price
+	LogBalanceOC      bool    `json:"BalanceOC"`      // uses opcode to query balance
+	LogGasPriceOC     bool    `json:"GasPriceOC"`     // uses opcode to query gas price
+	LogGasUsedFirst   float64 `json:"GasUsedFirst"`   // execute estimate gas
+	LogGasUsedSecond  float64 `json:"GasUsedSecond"`  // after execute gas
+	LogL2GasPrice     float64 `json:"L2GasPrice"`     // L2 gas price = LogL1GasPrice * l2GasPriceSugFactor
+	LogGasPrice       float64 `json:"GasPrice"`       // user gas price (signed) = L2 gas price
+	LogValueFirst     float64 `json:"ValueFirst"`     // effective gas price using LogGasUsedFirst (EGP)
+	LogValueSecond    float64 `json:"ValueSecond"`    // effective gas price using LogGasUsedSecond (NEGP)
+	LogValueFinal     float64 `json:"ValueFinal"`     // final gas price
+	LogReprocess      bool    `json:"Reprocess"`      // reprocessed (executed 2 times)
+	LogPercentage     uint64  `json:"Percentage"`     // user gas/final gas, coded percentage (0:not used, 1..255)
+	LogMaxDeviation   float64 `json:"MaxDeviation"`   // max allowed deviation = LogValueFirst * finalDeviationPct
+	LogFinalDeviation float64 `json:"FinalDeviation"` // final gas deviation = abs(LogValueSecond - LogValueFirst)
 }
 
 type egpStats struct {
-	totalTx          uint64 // Analyzed tx count
-	totalError       uint64 // EGP error tx count
-	totalNoInfo      uint64 // Empty egp_log tx count
-	totalEgp         uint64 // EGP enabled tx count
-	totalReprocessed uint64 // Reprocessed tx count
-	totalShady       uint64 // Suspicious tx count (used balance or gasprice opcodes)
-	totalUsedFirst   uint64 // Used final gas is the first EGP computed
-	totalUsedSecond  uint64 // Used final gas is the new EGP recomputed
-	totalUsedUser    uint64 // Used final gas is the user gas price signed
-	totalUsedWeird   uint64 // Used final gas is different from EGP, new EGP, and user
-	totalLossCount   uint64 // Loss gas tx count
-	totalLoss        uint64 // Total loss gas amount
-	sumGasFinal      uint64 // Accumulated sum of final gas (to get average)
-	countGasFinal    uint64 // Count number of accumulated (to get average)
-	sumGasPreEGP     uint64 // Accumulated sum of gas without EGP
-	countGasPreEGP   uint64 // Count number of accumulated pre EGP (to get average)
-	sumFee           uint64
-	sumFeePreEGP     uint64
+	totalTx          float64 // Analyzed tx count
+	totalError       float64 // EGP error tx count
+	totalNoInfo      float64 // Empty egp_log tx count
+	totalEgp         float64 // EGP enabled tx count
+	totalReprocessed float64 // Reprocessed tx count
+	totalShady       float64 // Suspicious tx count (used balance or gasprice opcodes)
+	totalUsedFirst   float64 // Used final gas is the first EGP computed
+	totalUsedSecond  float64 // Used final gas is the new EGP recomputed
+	totalUsedUser    float64 // Used final gas is the user gas price signed
+	totalUsedWeird   float64 // Used final gas is different from EGP, new EGP, and user
+	totalLossCount   float64 // Loss gas tx count
+	totalLoss        float64 // Total loss gas amount
+	sumGasFinal      float64 // Accumulated sum of final gas (to get average)
+	countGasFinal    float64 // Count number of accumulated (to get average)
+	sumGasPreEGP     float64 // Accumulated sum of gas without EGP
+	countGasPreEGP   float64 // Count number of accumulated pre EGP (to get average)
+	sumFee           float64
+	sumFeePreEGP     float64
 }
 
 func main() {
@@ -121,6 +122,11 @@ func main() {
 			Usage: "show full detail record when show loss/error",
 			Value: false,
 		},
+		&cli.BoolFlag{
+			Name:  "showalways",
+			Usage: "show full detail record always",
+			Value: false,
+		},
 		&cli.StringFlag{
 			Name:     "cfg",
 			Aliases:  []string{"c"},
@@ -221,6 +227,7 @@ func runStats(ctx *cli.Context) error {
 	showErrors = ctx.Bool("showerror")
 	showLosses = ctx.Bool("showloss")
 	showDetail = ctx.Bool("showdetail")
+	showAlways = ctx.Bool("showalways")
 
 	// Load simulation config file
 	var err error
@@ -344,18 +351,13 @@ func runStats(ctx *cli.Context) error {
 	return nil
 }
 
-// max calculates the maximum between 2 numbers
-// func max(a uint64, b uint64) uint64 {
-// 	if a > b {
-// 		return a
-// 	} else {
-// 		return b
-// 	}
-// }
-
 // countStats calculates and counts statistics for an EGP record
 func countStats(i uint64, block uint64, egp *egpLogRecord, stats *egpStats, cfg *egpConfig) {
-	// printEgpLogRecord(egp, false)
+	// Show record information
+	if showAlways {
+		printEgpLogRecord(egp, false)
+	}
+
 	// Total transactions
 	stats.totalTx++
 
@@ -415,12 +417,12 @@ func countStats(i uint64, block uint64, egp *egpLogRecord, stats *egpStats, cfg
 		}
 
 		stats.countGasPreEGP++
-		stats.sumGasPreEGP += uint64(float64(egp.LogL1GasPrice) * l2SugPreEGP)
-		stats.sumFeePreEGP += uint64(float64(egp.LogL1GasPrice) * l2SugPreEGP * float64(egp.LogGasUsedSecond))
+		stats.sumGasPreEGP += egp.LogL1GasPrice * l2SugPreEGP
+		stats.sumFeePreEGP += egp.LogL1GasPrice * l2SugPreEGP * egp.LogGasUsedSecond
 
 		// Loss
 		if egp.LogValueFinal == egp.LogGasPrice {
-			loss := uint64(0)
+			loss := float64(0)
 			if egp.LogReprocess {
 				if (egp.LogValueSecond-egp.LogValueFinal > 0) && (egp.LogValueFinal < egp.LogValueSecond) {
 					loss = egp.LogValueSecond - egp.LogValueFinal
@@ -435,8 +437,8 @@ func countStats(i uint64, block uint64, egp *egpLogRecord, stats *egpStats, cfg
 			stats.totalLoss += loss
 
 			if showLosses {
-				info := fmt.Sprintf("reprocess=%t, final=%d, egp1=%d, egp2=%d, user=%d", egp.LogReprocess, egp.LogValueFinal, egp.LogGasUsedFirst, egp.LogGasUsedSecond, egp.LogGasPrice)
-				fmt.Printf("egp-loss:#%d:(L2 block %d):loss=%d:info:%s\n", i, block, loss, info)
+				info := fmt.Sprintf("reprocess=%t, final=%.0f, egp1=%.0f, egp2=%.0f, user=%.0f", egp.LogReprocess, egp.LogValueFinal, egp.LogGasUsedFirst, egp.LogGasUsedSecond, egp.LogGasPrice)
+				fmt.Printf("egp-loss:#%d:(L2 block %d):loss=%.0f:info:%s\n", i, block, loss, info)
 				if showDetail {
 					printEgpLogRecord(egp, false)
 				}
@@ -457,20 +459,20 @@ func printEgpLogRecord(record *egpLogRecord, showTxInfo bool) {
 	fmt.Printf("  timestamp: [%v]\n", record.l2BlockReceived)
 	fmt.Printf("  Error: [%s]\n", record.LogError)
 	fmt.Printf("  Enabled: [%t]\n", record.LogEnabled)
-	fmt.Printf("  L1GasPrice: [%d]\n", record.LogL1GasPrice)
+	fmt.Printf("  L1GasPrice: [%.0f]\n", record.LogL1GasPrice)
 	fmt.Printf("  BalanceOC: [%t]\n", record.LogBalanceOC)
 	fmt.Printf("  GasPriceOC: [%t]\n", record.LogGasPriceOC)
-	fmt.Printf("  GasUsedFirst: [%d]\n", record.LogGasUsedFirst)
-	fmt.Printf("  GasUsedSecond: [%d]\n", record.LogGasUsedSecond)
-	fmt.Printf("  L2GasPrice: [%d]\n", record.LogL2GasPrice)
-	fmt.Printf("  GasPrice: [%d]\n", record.LogGasPrice)
-	fmt.Printf("  ValueFirst: [%d]\n", record.LogValueFirst)
-	fmt.Printf("  ValueSecond: [%d]\n", record.LogValueSecond)
-	fmt.Printf("  ValueFinal: [%d]\n", record.LogValueFinal)
+	fmt.Printf("  GasUsedFirst: [%.0f]\n", record.LogGasUsedFirst)
+	fmt.Printf("  GasUsedSecond: [%.0f]\n", record.LogGasUsedSecond)
+	fmt.Printf("  L2GasPrice: [%.0f]\n", record.LogL2GasPrice)
+	fmt.Printf("  GasPrice: [%.0f]\n", record.LogGasPrice)
+	fmt.Printf("  ValueFirst: [%.0f]\n", record.LogValueFirst)
+	fmt.Printf("  ValueSecond: [%.0f]\n", record.LogValueSecond)
+	fmt.Printf("  ValueFinal: [%.0f]\n", record.LogValueFinal)
 	fmt.Printf("  Reprocess: [%t]\n", record.LogReprocess)
 	fmt.Printf("  Percentage: [%d]\n", record.LogPercentage)
-	fmt.Printf("  MaxDeviation: [%d]\n", record.LogMaxDeviation)
-	fmt.Printf("  FinalDeviation: [%d]\n", record.LogFinalDeviation)
+	fmt.Printf("  MaxDeviation: [%.0f]\n", record.LogMaxDeviation)
+	fmt.Printf("  FinalDeviation: [%.0f]\n", record.LogFinalDeviation)
 	if showTxInfo {
 		fmt.Printf("  encoded: [%s]\n", record.encoded)
 	}
@@ -487,68 +489,60 @@ func printStats(stats *egpStats) {
 		ETH_DIV  = 1000000000000000000
 	)
 
-	fmt.Printf("Total Tx.........: [%d]\n", stats.totalTx)
+	fmt.Printf("Total Tx.........: [%.0f]\n", stats.totalTx)
 	if stats.totalTx == 0 {
 		return
 	}
 
-	fmt.Printf("Error Tx.........: [%d] (%.2f%%)\n", stats.totalError, float64(stats.totalError)/float64(stats.totalTx)*100)
-	fmt.Printf("Total No EGP info: [%d] (%.2f%%)\n", stats.totalNoInfo, float64(stats.totalNoInfo)/float64(stats.totalTx)*100)
+	fmt.Printf("Error Tx.........: [%.0f] (%.2f%%)\n", stats.totalError, stats.totalError/stats.totalTx*100)
+	fmt.Printf("Total No EGP info: [%.0f] (%.2f%%)\n", stats.totalNoInfo, stats.totalNoInfo/stats.totalTx*100)
 
 	statsCount := stats.totalTx - stats.totalNoInfo
-	fmt.Printf("Total Tx EGP info: [%d] (%.2f%%)\n", statsCount, float64(statsCount)/float64(stats.totalTx)*100)
+	fmt.Printf("Total Tx EGP info: [%.0f] (%.2f%%)\n", statsCount, statsCount/stats.totalTx*100)
 	if statsCount > 0 {
-		fmt.Printf("    EGP enable.......: [%d] (%.2f%%)\n", stats.totalEgp, float64(stats.totalEgp)/float64(statsCount)*100)
-		fmt.Printf("    Reprocessed Tx...: [%d] (%.2f%%)\n", stats.totalReprocessed, float64(stats.totalReprocessed)/float64(statsCount)*100)
+		fmt.Printf("    EGP enable.......: [%.0f] (%.2f%%)\n", stats.totalEgp, stats.totalEgp/statsCount*100)
+		fmt.Printf("    Reprocessed Tx...: [%.0f] (%.2f%%)\n", stats.totalReprocessed, stats.totalReprocessed/statsCount*100)
 		if stats.totalReprocessed > 0 {
-			fmt.Printf("        Suspicious Tx....: [%d] (%.2f%%)\n", stats.totalShady, float64(stats.totalShady)/float64(stats.totalReprocessed)*100)
+			fmt.Printf("        Suspicious Tx....: [%.0f] (%.2f%%)\n", stats.totalShady, stats.totalShady/stats.totalReprocessed*100)
 		} else {
-			fmt.Printf("        Suspicious Tx....: [%d] (0.00%%)\n", stats.totalShady)
+			fmt.Printf("        Suspicious Tx....: [%.0f] (0.00%%)\n", stats.totalShady)
 		}
 		fmt.Printf("    Final gas:\n")
-		fmt.Printf("        Used EGP1........: [%d] (%.2f%%)\n", stats.totalUsedFirst, float64(stats.totalUsedFirst)/float64(statsCount)*100)
-		fmt.Printf("        Used EGP2........: [%d] (%.2f%%)\n", stats.totalUsedSecond, float64(stats.totalUsedSecond)/float64(statsCount)*100)
-		fmt.Printf("        Used User Gas....: [%d] (%.2f%%)\n", stats.totalUsedUser, float64(stats.totalUsedUser)/float64(statsCount)*100)
-		fmt.Printf("        Used Weird Gas...: [%d] (%.2f%%)\n", stats.totalUsedWeird, float64(stats.totalUsedWeird)/float64(statsCount)*100)
+		fmt.Printf("        Used EGP1........: [%.0f] (%.2f%%)\n", stats.totalUsedFirst, stats.totalUsedFirst/statsCount*100)
+		fmt.Printf("        Used EGP2........: [%.0f] (%.2f%%)\n", stats.totalUsedSecond, stats.totalUsedSecond/statsCount*100)
+		fmt.Printf("        Used User Gas....: [%.0f] (%.2f%%)\n", stats.totalUsedUser, stats.totalUsedUser/statsCount*100)
+		fmt.Printf("        Used Weird Gas...: [%.0f] (%.2f%%)\n", stats.totalUsedWeird, stats.totalUsedWeird/statsCount*100)
 		if stats.countGasFinal > 0 {
-			fmt.Printf("    Gas price avg........: [%d] (%.3f GWei) (%.9f ETH)\n", stats.sumGasFinal/stats.countGasFinal,
-				float64(stats.sumGasFinal/stats.countGasFinal)/GWEI_DIV, float64(stats.sumGasFinal/stats.countGasFinal)/ETH_DIV)
+			fmt.Printf("    Gas price avg........: [%.0f] (%.3f GWei) (%.9f ETH)\n", stats.sumGasFinal/stats.countGasFinal,
+				stats.sumGasFinal/stats.countGasFinal/GWEI_DIV, stats.sumGasFinal/stats.countGasFinal/ETH_DIV)
 		}
 		if stats.countGasFinal > 0 {
-			fmt.Printf("    Tx fee avg...........: [%d] (%.3f GWei) (%.9f ETH)\n", stats.sumFee/stats.countGasFinal,
-				float64(stats.sumFee/stats.countGasFinal)/GWEI_DIV, float64(stats.sumFee/stats.countGasFinal)/ETH_DIV)
+			fmt.Printf("    Tx fee avg...........: [%.0f] (%.3f GWei) (%.9f ETH)\n", stats.sumFee/stats.countGasFinal,
+				stats.sumFee/stats.countGasFinal/GWEI_DIV, stats.sumFee/stats.countGasFinal/ETH_DIV)
 		}
 		if stats.countGasPreEGP > 0 {
-			fmt.Printf("    Gas pri.avg preEGP...: [%d] (%.3f GWei) (%.9f ETH)\n", stats.sumGasPreEGP/stats.countGasPreEGP,
-				float64(stats.sumGasPreEGP/stats.countGasPreEGP)/GWEI_DIV, float64(stats.sumGasPreEGP/stats.countGasPreEGP)/ETH_DIV)
+			fmt.Printf("    Gas pri.avg preEGP...: [%.0f] (%.3f GWei) (%.9f ETH)\n", stats.sumGasPreEGP/stats.countGasPreEGP,
+				stats.sumGasPreEGP/stats.countGasPreEGP/GWEI_DIV, stats.sumGasPreEGP/stats.countGasPreEGP/ETH_DIV)
 		}
 		if stats.countGasPreEGP > 0 {
-			fmt.Printf("    Tx fee avg preEGP....: [%d] (%.3f GWei) (%.9f ETH)\n", stats.sumFeePreEGP/stats.countGasPreEGP,
-				float64(stats.sumFeePreEGP/stats.countGasPreEGP)/GWEI_DIV, float64(stats.sumFeePreEGP/stats.countGasPreEGP)/ETH_DIV)
-		}
-		fmt.Printf("    Diff fee EGP-preEGP..: [%d] (%.3f Gwei) (%.9f ETH)\n", int64(stats.sumFee-stats.sumFeePreEGP),
-			float64(int64(stats.sumFee-stats.sumFeePreEGP))/GWEI_DIV, float64(int64(stats.sumFee-stats.sumFeePreEGP))/ETH_DIV)
-		fmt.Printf("    Loss count.......: [%d] (%.2f%%)\n", stats.totalLossCount, float64(stats.totalLossCount)/float64(statsCount)*100)
-		if stats.totalLoss < GWEI_DIV*10 {
-			fmt.Printf("    Loss total.......: [%d] (%d KWei)\n", stats.totalLoss, stats.totalLoss/1000)
-		} else {
-			fmt.Printf("    Loss total.......: [%d] (%d GWei) (%.9f ETH)\n", stats.totalLoss, stats.totalLoss/GWEI_DIV, float64(stats.totalLoss)/ETH_DIV)
+			fmt.Printf("    Tx fee avg preEGP....: [%.0f] (%.3f GWei) (%.9f ETH)\n", stats.sumFeePreEGP/stats.countGasPreEGP,
+				stats.sumFeePreEGP/stats.countGasPreEGP/GWEI_DIV, stats.sumFeePreEGP/stats.countGasPreEGP/ETH_DIV)
 		}
+		fmt.Printf("    Diff fee EGP-preEGP..: [%.0f] (%.3f Gwei) (%.9f ETH)\n", stats.sumFee-stats.sumFeePreEGP,
+			(stats.sumFee-stats.sumFeePreEGP)/GWEI_DIV, (stats.sumFee-stats.sumFeePreEGP)/ETH_DIV)
+		fmt.Printf("    Loss count.......: [%.0f] (%.2f%%)\n", stats.totalLossCount, stats.totalLossCount/statsCount*100)
+		fmt.Printf("    Loss total.......: [%.0f] (%.3f GWei) (%.9f ETH)\n", stats.totalLoss, stats.totalLoss/GWEI_DIV, stats.totalLoss/ETH_DIV)
 		if stats.totalLossCount > 0 {
-			if stats.totalLoss/stats.totalLossCount < GWEI_DIV*10 {
-				fmt.Printf("    Loss average.....: [%d] (%d KWei)\n", stats.totalLoss/stats.totalLossCount, stats.totalLoss/stats.totalLossCount/1000)
-			} else {
-				fmt.Printf("    Loss average.....: [%d] (%d GWei) (%.9f ETH)\n", stats.totalLoss/stats.totalLossCount, stats.totalLoss/stats.totalLossCount/GWEI_DIV,
-					float64(stats.totalLoss/stats.totalLossCount)/ETH_DIV)
-			}
+			fmt.Printf("    Loss average.....: [%.0f] (%.0f GWei) (%.9f ETH)\n", stats.totalLoss/stats.totalLossCount, stats.totalLoss/stats.totalLossCount/GWEI_DIV,
+				stats.totalLoss/stats.totalLossCount/ETH_DIV)
 		}
 	}
 }
 
 // simulateConfig simulates scenario using received config
 func simulateConfig(egp *egpLogRecord, cfg *egpConfig) {
 	// L2 and user gas price
-	egp.LogL2GasPrice = uint64(float64(egp.LogL1GasPrice) * cfg.L2GasPriceSugFactor)
+	egp.LogL2GasPrice = egp.LogL1GasPrice * cfg.L2GasPriceSugFactor
 	egp.LogGasPrice = egp.LogL2GasPrice
 
 	// Compute EGP
@@ -569,8 +563,8 @@ func simulateConfig(egp *egpLogRecord, cfg *egpConfig) {
 		}
 
 		// Gas price deviation
-		egp.LogFinalDeviation = uint64(math.Abs(float64(int64(egp.LogValueSecond) - int64(egp.LogValueFirst))))
-		egp.LogMaxDeviation = egp.LogValueFirst * cfg.FinalDeviationPct / 100
+		egp.LogFinalDeviation = math.Abs(egp.LogValueSecond - egp.LogValueFirst)
+		egp.LogMaxDeviation = egp.LogValueFirst * float64(cfg.FinalDeviationPct) / 100
 
 		if egp.LogFinalDeviation < egp.LogMaxDeviation {
 			// Final gas: EGP
@@ -594,18 +588,18 @@ func simulateConfig(egp *egpLogRecord, cfg *egpConfig) {
 
 	// Gas price effective percentage
 	if egp.LogGasPrice > 0 {
-		egp.LogPercentage = ((egp.LogValueFinal*256)+egp.LogGasPrice-1)/egp.LogGasPrice - 1
+		egp.LogPercentage = uint64(((egp.LogValueFinal*256)+egp.LogGasPrice-1)/egp.LogGasPrice - 1)
 	} else {
 		egp.LogPercentage = 0
 	}
 }
 
 // calcEffectiveGasPrice calculates the effective gas price
-func calcEffectiveGasPrice(gasUsed uint64, tx *egpLogRecord, cfg *egpConfig) (uint64, error) {
+func calcEffectiveGasPrice(gasUsed float64, tx *egpLogRecord, cfg *egpConfig) (float64, error) {
 	// Calculate break even gas price
 	var breakEvenGasPrice float64
 	if gasUsed == 0 {
-		breakEvenGasPrice = float64(tx.LogGasPrice)
+		breakEvenGasPrice = tx.LogGasPrice
 	} else {
 		// Decode tx
 		rawBytes, err := decodeTx(tx)
@@ -616,27 +610,26 @@ func calcEffectiveGasPrice(gasUsed uint64, tx *egpLogRecord, cfg *egpConfig) (ui
 		// Zero and non zero bytes
 		txZeroBytes := uint64(bytes.Count(rawBytes, []byte{0}))
 		txNonZeroBytes := uint64(len(rawBytes)) - txZeroBytes
-		// logf("size: %d", len(rawBytes))
 
 		// Calculates break even gas price
-		l2MinGasPrice := float64(tx.LogL1GasPrice) * cfg.L1GasPriceFactor
+		l2MinGasPrice := tx.LogL1GasPrice * cfg.L1GasPriceFactor
 		if l2MinGasPrice < float64(cfg.MinGasPriceAllowed) {
 			l2MinGasPrice = float64(cfg.MinGasPriceAllowed)
 		}
-		totalTxPrice := float64(gasUsed)*l2MinGasPrice + float64(((fixedBytesTx+txNonZeroBytes)*cfg.ByteGasCost+txZeroBytes*cfg.ZeroGasCost)*tx.LogL1GasPrice)
-		breakEvenGasPrice = totalTxPrice / float64(gasUsed) * cfg.NetProfitFactor
+		totalTxPrice := gasUsed*l2MinGasPrice + float64((fixedBytesTx+txNonZeroBytes)*cfg.ByteGasCost+txZeroBytes*cfg.ZeroGasCost)*tx.LogL1GasPrice
+		breakEvenGasPrice = totalTxPrice / gasUsed * cfg.NetProfitFactor
 	}
 
 	// Calculate effective gas price
 	var ratioPriority float64
 	if tx.LogGasPrice > tx.LogL2GasPrice {
-		ratioPriority = math.Round(float64(tx.LogGasPrice / tx.LogL2GasPrice))
+		ratioPriority = math.Round(tx.LogGasPrice / tx.LogL2GasPrice)
 	} else {
 		ratioPriority = 1
 	}
 	effectiveGasPrice := breakEvenGasPrice * ratioPriority
 
-	return uint64(effectiveGasPrice), nil
+	return effectiveGasPrice, nil
 }
 
 // decodeTx decodes the encoded tx
```
