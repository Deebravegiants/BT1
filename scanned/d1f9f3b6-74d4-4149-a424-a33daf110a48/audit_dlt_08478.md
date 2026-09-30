# [?] Prevent panics by metrics calls from crashing the process (#2140)

## Summary
Severity: Unknown
Chain: Sei
Component: sei-protocol/sei-chain
Published: 2025-06-24
Source: https://github.com/sei-protocol/sei-chain/commit/4fac51f02838fb683f83a9530b541c2729b16c00
Type: security-commit

## Details
Prevent panics by metrics calls from crashing the process (#2140)

## Patch
### app/invariance.go
```diff
@@ -13,6 +13,8 @@ import (
 
 	bankkeeper "github.com/cosmos/cosmos-sdk/x/bank/keeper"
 	banktypes "github.com/cosmos/cosmos-sdk/x/bank/types"
+
+	seimetrics "github.com/sei-protocol/sei-chain/utils/metrics"
 )
 
 type LightInvarianceConfig struct {
@@ -60,7 +62,7 @@ func (app *App) LightInvarianceTotalSupply(cms sdk.CommitMultiStore) {
 	for _, p := range balanceChangePairs {
 		if len(p.Key) < 2 {
 			// invalid key; ignore
-			metrics.IncrCounterWithLabels([]string{"sei", "lightinvariance_supply", "invalid_changed_key"}, 1, []metrics.Label{
+			seimetrics.SafeMetricsIncrCounterWithLabels([]string{"sei", "lightinvariance_supply", "invalid_changed_key"}, 1, []metrics.Label{
 				{
 					Name:  "type",
 					Value: "sei",
@@ -72,7 +74,7 @@ func (app *App) LightInvarianceTotalSupply(cms sdk.CommitMultiStore) {
 		addrLen := int(p.Key[1])
 		if len(p.Key) < addrLen+2 {
 			// invalid key length; ignore
-			metrics.IncrCounterWithLabels([]string{"sei", "lightinvariance_supply", "invalid_changed_key"}, 1, []metrics.Label{
+			seimetrics.SafeMetricsIncrCounterWithLabels([]string{"sei", "lightinvariance_supply", "invalid_changed_key"}, 1, []metrics.Label{
 				{
 					Name:  "type",
 					Value: "sei",
@@ -89,7 +91,7 @@ func (app *App) LightInvarianceTotalSupply(cms sdk.CommitMultiStore) {
 		if !p.Delete {
 			var balance sdk.Coin
 			if err := balance.Unmarshal(p.Value); err != nil {
-				metrics.IncrCounterWithLabels([]string{"sei", "lightinvariance_supply", "unmarshal_failure"}, 1, []metrics.Label{
+				seimetrics.SafeMetricsIncrCounterWithLabels([]string{"sei", "lightinvariance_supply", "unmarshal_failure"}, 1, []metrics.Label{
 					{
 						Name:  "type",
 						Value: "usei",
@@ -117,7 +119,7 @@ func (app *App) LightInvarianceTotalSupply(cms sdk.CommitMultiStore) {
 		}
 		var balance sdk.Coin
 		if err := balance.Unmarshal(val); err != nil {
-			metrics.IncrCounterWithLabels([]string{"sei", "lightinvariance_supply", "unmarshal_failure"}, 1, []metrics.Label{
+			seimetrics.SafeMetricsIncrCounterWithLabels([]string{"sei", "lightinvariance_supply", "unmarshal_failure"}, 1, []metrics.Label{
 				{
 					Name:  "type",
 					Value: "usei",
@@ -137,7 +139,7 @@ func (app *App) LightInvarianceTotalSupply(cms sdk.CommitMultiStore) {
 	for _, p := range weiChangePairs {
 		var amt sdk.Int
 		if len(p.Key) < 1 {
-			metrics.IncrCounterWithLabels([]string{"sei", "lightinvariance_supply", "invalid_changed_key"}, 1, []metrics.Label{
+			seimetrics.SafeMetricsIncrCounterWithLabels([]string{"sei", "lightinvariance_supply", "invalid_changed_key"}, 1, []metrics.Label{
 				{
 					Name:  "type",
 					Value: "wei",
@@ -148,7 +150,7 @@ func (app *App) LightInvarianceTotalSupply(cms sdk.CommitMultiStore) {
 		}
 		if !p.Delete {
 			if err := amt.Unmarshal(p.Value); err != nil {
-				metrics.IncrCounterWithLabels([]string{"sei", "lightinvariance_supply", "unmarshal_failure"}, 1, []metrics.Label{
+				seimetrics.SafeMetricsIncrCounterWithLabels([]string{"sei", "lightinvariance_supply", "unmarshal_failure"}, 1, []metrics.Label{
 					{
 						Name:  "type",
 						Value: "wei",
@@ -176,7 +178,7 @@ func (app *App) LightInvarianceTotalSupply(cms sdk.CommitMultiStore) {
 		}
 		var amt sdk.Int
 		if err := amt.Unmarshal(val); err != nil {
-			metrics.IncrCounterWithLabels([]string{"sei", "lightinvariance_supply", "unmarshal_failure"}, 1, []metrics.Label{
+			seimetrics.SafeMetricsIncrCounterWithLabels([]string{"sei", "lightinvariance_supply", "unmarshal_failure"}, 1, []metrics.Label{
 				{
 					Name:  "type",
 					Value: "wei",
@@ -196,7 +198,7 @@ func (app *App) LightInvarianceTotalSupply(cms sdk.CommitMultiStore) {
 	if bz := ckv.Get(append(banktypes.SupplyKey, []byte(sdk.MustGetBaseDenom())...)); bz != nil {
 		var amt sdk.Int
 		if err := amt.Unmarshal(bz); err != nil {
-			metrics.IncrCounterWithLabels([]string{"sei", "lightinvariance_supply", "unmarshal_failure"}, 1, []metrics.Label{
+			seimetrics.SafeMetricsIncrCounterWithLabels([]string{"sei", "lightinvariance_supply", "unmarshal_failure"}, 1, []metrics.Label{
 				{
 					Name:  "type",
 					Value: "total_supply",
@@ -217,7 +219,7 @@ func (app *App) LightInvarianceTotalSupply(cms sdk.CommitMultiStore) {
 			} else {
 				var amt sdk.Int
 				if err := amt.Unmarshal(p.Value); err != nil {
-					metrics.IncrCounterWithLabels([]string{"sei", "lightinvariance_supply", "unmarshal_failure"}, 1, []metrics.Label{
+					seimetrics.SafeMetricsIncrCounterWithLabels([]string{"sei", "lightinvariance_supply", "unmarshal_failure"}, 1, []metrics.Label{
 						{
 							Name:  "type",
 							Value: "total_supply",
```

### oracle/price-feeder/oracle/filter.go
```diff
@@ -2,11 +2,11 @@ package oracle
 
 import (
 	"github.com/armon/go-metrics"
-	"github.com/cosmos/cosmos-sdk/telemetry"
 	sdk "github.com/cosmos/cosmos-sdk/types"
 	"github.com/rs/zerolog"
 
 	"github.com/sei-protocol/sei-chain/oracle/price-feeder/oracle/provider"
+	seimetrics "github.com/sei-protocol/sei-chain/utils/metrics"
 )
 
 // defaultDeviationThreshold defines how many 𝜎 a provider can be away
@@ -60,7 +60,7 @@ func FilterTickerDeviations(
 				}
 				p[base] = tp
 			} else {
-				telemetry.IncrCounterWithLabels([]string{"failure", "provider"}, 1, []metrics.Label{
+				seimetrics.SafeTelemetryIncrCounterWithLabels([]string{"failure", "provider"}, 1, []metrics.Label{
 					{Name: "type", Value: "ticker"},
 					{Name: "reason", Value: "deviation"},
 					{Name: "base", Value: base},
@@ -139,7 +139,7 @@ func FilterCandleDeviations(
 				}
 				p[base] = candles[providerName][base]
 			} else {
-				telemetry.IncrCounterWithLabels([]string{"failure", "provider"}, 1, []metrics.Label{
+				seimetrics.SafeTelemetryIncrCounterWithLabels([]string{"failure", "provider"}, 1, []metrics.Label{
 					{Name: "type", Value: "candle"},
 					{Name: "reason", Value: "deviation"},
 					{Name: "base", Value: base},
```

### oracle/price-feeder/oracle/oracle.go
```diff
@@ -9,7 +9,7 @@ import (
 	"sync"
 	"time"
 
-	"github.com/armon/go-metrics"
+	gometrics "github.com/armon/go-metrics"
 	sdkclient "github.com/cosmos/cosmos-sdk/client"
 	"github.com/cosmos/cosmos-sdk/telemetry"
 	sdk "github.com/cosmos/cosmos-sdk/types"
@@ -23,6 +23,7 @@ import (
 	"github.com/sei-protocol/sei-chain/oracle/price-feeder/oracle/provider"
 	"github.com/sei-protocol/sei-chain/oracle/price-feeder/oracle/types"
 	pfsync "github.com/sei-protocol/sei-chain/oracle/price-feeder/pkg/sync"
+	seimetrics "github.com/sei-protocol/sei-chain/utils/metrics"
 	oracletypes "github.com/sei-protocol/sei-chain/x/oracle/types"
 )
 
@@ -138,18 +139,18 @@ func (o *Oracle) Start(ctx context.Context) error {
 			startTime := time.Now()
 			err = o.tick(ctx, clientCtx, currBlockHeight)
 			if err != nil {
-				telemetry.IncrCounter(1, "failure", "tick")
+				seimetrics.SafeTelemetryIncrCounter(1, "failure", "tick")
 				o.logger.Warn().Msg(fmt.Sprintf("Oracle tick failed for height %d, err: %s", currBlockHeight, err.Error()))
 			} else {
-				telemetry.IncrCounter(1, "success", "tick")
+				seimetrics.SafeTelemetryIncrCounter(1, "success", "tick")
 			}
 			telemetry.MeasureSince(startTime, "latency", "tick")
-			telemetry.IncrCounter(1, "num_ticks", "tick")
+			seimetrics.SafeTelemetryIncrCounter(1, "num_ticks", "tick")
 
 			// Catch any missing blocks
 			if currBlockHeight > (previousBlockHeight+1) && previousBlockHeight > 0 {
 				missedBlocks := currBlockHeight - (previousBlockHeight + 1)
-				telemetry.IncrCounter(float32(missedBlocks), "skipped_blocks", "tick")
+				seimetrics.SafeTelemetryIncrCounter(float32(missedBlocks), "skipped_blocks", "tick")
 			}
 			previousBlockHeight = currBlockHeight
 		}
@@ -203,7 +204,7 @@ func safeMapContains[V any](m map[string]V, key string) bool {
 func reportPriceErrMetrics[V any](providerName string, priceType string, prices map[string]V, expected []types.CurrencyPair) {
 	for _, pair := range expected {
 		if !safeMapContains(prices, pair.String()) {
-			sendProviderFailureMetric([]string{"failure", "provider"}, 1, []metrics.Label{
+			sendProviderFailureMetric([]string{"failure", "provider"}, 1, []gometrics.Label{
 				{Name: "type", Value: priceType},
 				{Name: "reason", Value: "error"},
 				{Name: "provider", Value: providerName},
@@ -234,7 +235,7 @@ func (o *Oracle) SetPrices(ctx context.Context) error {
 
 		priceProvider, err := o.getOrSetProvider(ctx, providerName)
 		if err != nil {
-			sendProviderFailureMetric([]string{"failure", "provider"}, 1, []metrics.Label{
+			sendProviderFailureMetric([]string{"failure", "provider"}, 1, []gometrics.Label{
 				{Name: "reason", Value: "init"},
 				{Name: "provider", Value: providerName},
 			})
@@ -274,7 +275,7 @@ func (o *Oracle) SetPrices(ctx context.Context) error {
 			case <-ch:
 				break
 			case <-time.After(o.providerTimeout):
-				telemetry.IncrCounterWithLabels([]string{"failure", "provider"}, 1, []metrics.Label{
+				seimetrics.SafeTelemetryIncrCounterWithLabels([]string{"failure", "provider"}, 1, []gometrics.Label{
 					{Name: "reason", Value: "timeout"},
 					{Name: "provider", Value: providerName},
 				})
@@ -291,7 +292,7 @@ func (o *Oracle) SetPrices(ctx context.Context) error {
 				success := SetProviderTickerPricesAndCandles(providerName, providerPrices, providerCandles, prices, candles, pair)
 				if !success {
 					mtx.Unlock()
-					telemetry.IncrCounterWithLabels([]string{"failure", "provider"}, 1, []metrics.Label{
+					seimetrics.SafeTelemetryIncrCounterWithLabels([]string{"failure", "provider"}, 1, []gometrics.Label{
 						{Name: "reason", Value: "set-prices"},
 						{Name: "provider", Value: providerName},
 					})
@@ -702,7 +703,7 @@ func (o *Oracle) tick(
 	resp, err := o.oracleClient.BroadcastTx(clientCtx, voteMsg)
 	if err != nil {
 		o.logResponseError(err, resp, startTime, blockHeight)
-		telemetry.IncrCounter(1, "failure", "broadcast")
+		seimetrics.SafeTelemetryIncrCounter(1, "failure", "broadcast")
 		return err
 	}
 
@@ -712,7 +713,7 @@ func (o *Oracle) tick(
 		Str("tx_hash", resp.TxHash).
 		Int64("tick_duration", time.Since(startTime).Milliseconds()).
 		Msg(fmt.Sprintf("broadcasted for height %d", blockHeight))
-	telemetry.IncrCounter(1, "success", "broadcast")
+	seimetrics.SafeTelemetryIncrCounter(1, "success", "broadcast")
 
 	o.previousVotePeriod = currentVotePeriod
 	o.healthchecksPing()
```

### oracle/price-feeder/oracle/provider/binance.go
```diff
@@ -12,8 +12,8 @@ import (
 
 	"github.com/sei-protocol/sei-chain/oracle/price-feeder/config"
 	"github.com/sei-protocol/sei-chain/oracle/price-feeder/oracle/types"
+	"github.com/sei-protocol/sei-chain/utils/metrics"
 
-	"github.com/cosmos/cosmos-sdk/telemetry"
 	"github.com/gorilla/websocket"
 	"github.com/rs/zerolog"
 )
@@ -266,7 +266,7 @@ func (p *BinanceProvider) messageReceived(messageType int, bz []byte) {
 	tickerErr = json.Unmarshal(bz, &tickerResp)
 	if len(tickerResp.LastPrice) != 0 {
 		p.setTickerPair(tickerResp)
-		telemetry.IncrCounter(
+		metrics.SafeTelemetryIncrCounter(
 			1,
 			"websocket",
 			"message",
@@ -281,7 +281,7 @@ func (p *BinanceProvider) messageReceived(messageType int, bz []byte) {
 	candleErr = json.Unmarshal(bz, &candleResp)
 	if len(candleResp.Metadata.Close) != 0 {
 		p.setCandlePair(candleResp)
-		telemetry.IncrCounter(
+		metrics.SafeTelemetryIncrCounter(
 			1,
 			"websocket",
 			"message",
@@ -384,7 +384,7 @@ func (p *BinanceProvider) reconnect() error {
 
 	currencyPairs := p.subscribedPairsToSlice()
 
-	telemetry.IncrCounter(
+	metrics.SafeTelemetryIncrCounter(
 		1,
 		"websocket",
 		"reconnect",
```

### oracle/price-feeder/oracle/provider/coinbase.go
```diff
@@ -16,8 +16,8 @@ import (
 
 	"github.com/sei-protocol/sei-chain/oracle/price-feeder/config"
 	"github.com/sei-protocol/sei-chain/oracle/price-feeder/oracle/types"
+	"github.com/sei-protocol/sei-chain/utils/metrics"
 
-	"github.com/cosmos/cosmos-sdk/telemetry"
 	sdk "github.com/cosmos/cosmos-sdk/types"
 )
 
@@ -242,7 +242,7 @@ func (p *CoinbaseProvider) SubscribeCurrencyPairs(cps ...types.CurrencyPair) err
 	}
 
 	p.setSubscribedPairs(cps...)
-	telemetry.IncrCounter(
+	metrics.SafeTelemetryIncrCounter(
 		float32(len(cps)),
 		"websocket",
 		"subscribe",
@@ -387,7 +387,7 @@ func (p *CoinbaseProvider) messageReceived(messageType int, bz []byte) {
 		}
 
 		p.setTickerPair(coinbaseTicker)
-		telemetry.IncrCounter(
+		metrics.SafeTelemetryIncrCounter(
 			1,
 			"websocket",
 			"message",
@@ -398,7 +398,7 @@ func (p *CoinbaseProvider) messageReceived(messageType int, bz []byte) {
 		)
 		return
 	}
-	telemetry.IncrCounter(
+	metrics.SafeTelemetryIncrCounter(
 		1,
 		"websocket",
 		"message",
@@ -501,7 +501,7 @@ func (p *CoinbaseProvider) reconnect() error {
 
 	currencyPairs := p.subscribedPairsToSlice()
 
-	telemetry.IncrCounter(
+	metrics.SafeTelemetryIncrCounter(
 		1,
 		"websocket",
 		"reconnect",
```

### oracle/price-feeder/oracle/provider/crypto.go
```diff
@@ -10,11 +10,11 @@ import (
 	"sync"
 	"time"
 
-	"github.com/cosmos/cosmos-sdk/telemetry"
 	"github.com/gorilla/websocket"
 	"github.com/rs/zerolog"
 	"github.com/sei-protocol/sei-chain/oracle/price-feeder/config"
 	"github.com/sei-protocol/sei-chain/oracle/price-feeder/oracle/types"
+	"github.com/sei-protocol/sei-chain/utils/metrics"
 )
 
 const (
@@ -274,7 +274,7 @@ func (p *CryptoProvider) messageReceived(messageType int, bz []byte) {
 	if tickerResp.Result.Channel == cryptoTickerChannel {
 		for _, tickerPair := range tickerResp.Result.Data {
 			p.setTickerPair(tickerResp.Result.InstrumentName, tickerPair)
-			telemetry.IncrCounter(
+			metrics.SafeTelemetryIncrCounter(
 				1,
 				"websocket",
 				"message",
@@ -291,7 +291,7 @@ func (p *CryptoProvider) messageReceived(messageType int, bz []byte) {
 	if candleResp.Result.Channel == cryptoCandleChannel {
 		for _, candlePair := range candleResp.Result.Data {
 			p.setCandlePair(candleResp.Result.InstrumentName, candlePair)
-			telemetry.IncrCounter(
+			metrics.SafeTelemetryIncrCounter(
 				1,
 				"websocket",
 				"message",
```

### oracle/price-feeder/oracle/provider/gate.go
```diff
@@ -11,12 +11,12 @@ import (
 	"sync"
 	"time"
 
-	"github.com/cosmos/cosmos-sdk/telemetry"
 	"github.com/gorilla/websocket"
 	"github.com/rs/zerolog"
 
 	"github.com/sei-protocol/sei-chain/oracle/price-feeder/config"
 	"github.com/sei-protocol/sei-chain/oracle/price-feeder/oracle/types"
+	"github.com/sei-protocol/sei-chain/utils/metrics"
 )
 
 const (
@@ -263,7 +263,7 @@ func (p *GateProvider) SubscribeCurrencyPairs(cps ...types.CurrencyPair) error {
 		return err
 	}
 	p.setSubscribedPairs(cps...)
-	telemetry.IncrCounter(
+	metrics.SafeTelemetryIncrCounter(
 		float32(len(cps)),
 		"websocket",
 		"subscribe",
@@ -430,7 +430,7 @@ func (p *GateProvider) messageReceivedTickerPrice(bz []byte) error {
 	}
 
 	p.setTickerPair(gateTicker)
-	telemetry.IncrCounter(
+	metrics.SafeTelemetryIncrCounter(
 		1,
 		"websocket",
 		"message",
@@ -512,7 +512,7 @@ func (p *GateProvider) messageReceivedCandle(bz []byte) error {
 	}
 
 	p.setCandlePair(gateCandle)
-	telemetry.IncrCounter(
+	metrics.SafeTelemetryIncrCounter(
 		1,
 		"websocket",
 		"message",
@@ -599,7 +599,7 @@ func (p *GateProvider) reconnect() error {
 
 	currencyPairs := p.subscribedPairsToSlice()
 
-	telemetry.IncrCounter(
+	metrics.SafeTelemetryIncrCounter(
 		1,
 		"websocket",
 		"reconnect",
```

### oracle/price-feeder/oracle/provider/huobi.go
```diff
@@ -16,8 +16,8 @@ import (
 
 	"github.com/sei-protocol/sei-chain/oracle/price-feeder/config"
 	"github.com/sei-protocol/sei-chain/oracle/price-feeder/oracle/types"
+	"github.com/sei-protocol/sei-chain/utils/metrics"
 
-	"github.com/cosmos/cosmos-sdk/telemetry"
 	"github.com/gorilla/websocket"
 	"github.com/rs/zerolog"
 )
@@ -187,7 +187,7 @@ func (p *HuobiProvider) SubscribeCurrencyPairs(cps ...types.CurrencyPair) error
 	}
 
 	p.setSubscribedPairs(cps...)
-	telemetry.IncrCounter(
+	metrics.SafeTelemetryIncrCounter(
 		float32(len(cps)),
 		"websocket",
 		"subscribe",
@@ -302,7 +302,7 @@ func (p *HuobiProvider) messageReceived(messageType int, bz []byte, reconnectTic
 	tickerErr = json.Unmarshal(bz, &tickerResp)
 	if tickerResp.Tick.LastPrice != 0 {
 		p.setTickerPair(tickerResp)
-		telemetry.IncrCounter(
+		metrics.SafeTelemetryIncrCounter(
 			1,
 			"websocket",
 			"message",
@@ -317,7 +317,7 @@ func (p *HuobiProvider) messageReceived(messageType int, bz []byte, reconnectTic
 	candleErr = json.Unmarshal(bz, &candleResp)
 	if candleResp.Tick.Close != 0 {
 		p.setCandlePair(candleResp)
-		telemetry.IncrCounter(
+		metrics.SafeTelemetryIncrCounter(
 			1,
 			"websocket",
 			"message",
@@ -406,7 +406,7 @@ func (p *HuobiProvider) reconnect() error {
 
 	currencyPairs := p.subscribedPairsToSlice()
 
-	telemetry.IncrCounter(
+	metrics.SafeTelemetryIncrCounter(
 		1,
 		"websocket",
 		"reconnect",
```

### oracle/price-feeder/oracle/provider/kraken.go
```diff
@@ -13,8 +13,8 @@ import (
 
 	"github.com/sei-protocol/sei-chain/oracle/price-feeder/config"
 	"github.com/sei-protocol/sei-chain/oracle/price-feeder/oracle/types"
+	"github.com/sei-protocol/sei-chain/utils/metrics"
 
-	"github.com/cosmos/cosmos-sdk/telemetry"
 	"github.com/gorilla/websocket"
 	"github.com/rs/zerolog"
 )
@@ -199,7 +199,7 @@ func (p *KrakenProvider) SubscribeCurrencyPairs(cps ...types.CurrencyPair) error
 	}
 
 	p.setSubscribedPairs(cps...)
-	telemetry.IncrCounter(
+	metrics.SafeTelemetryIncrCounter(
 		float32(len(cps)),
 		"websocket",
 		"subscribe",
@@ -396,7 +396,7 @@ func (p *KrakenProvider) messageReceivedTickerPrice(bz []byte) error {
 	}
 
 	p.setTickerPair(currencyPairSymbol, tickerPrice)
-	telemetry.IncrCounter(
+	metrics.SafeTelemetryIncrCounter(
 		1,
 		"websocket",
 		"message",
@@ -480,7 +480,7 @@ func (p *KrakenProvider) messageReceivedCandle(bz []byte) error {
 	currencyPairSymbol := krakenPairToCurrencyPairSymbol(krakenPair)
 	krakenCandle.Symbol = currencyPairSymbol
 
-	telemetry.IncrCounter(
+	metrics.SafeTelemetryIncrCounter(
 		1,
 		"websocket",
 		"message",
@@ -511,7 +511,7 @@ func (p *KrakenProvider) reconnect() error {
 
 	currencyPairs := p.subscribedPairsToSlice()
 
-	telemetry.IncrCounter(
+	metrics.SafeTelemetryIncrCounter(
 		1,
 		"websocket",
 		"reconnect",
```

### oracle/price-feeder/oracle/provider/mexc.go
```diff
@@ -13,8 +13,8 @@ import (
 
 	"github.com/sei-protocol/sei-chain/oracle/price-feeder/config"
 	"github.com/sei-protocol/sei-chain/oracle/price-feeder/oracle/types"
+	"github.com/sei-protocol/sei-chain/utils/metrics"
 
-	"github.com/cosmos/cosmos-sdk/telemetry"
 	"github.com/gorilla/websocket"
 	"github.com/rs/zerolog"
 )
@@ -287,7 +287,7 @@ func (p *MexcProvider) messageReceived(messageType int, bz []byte) {
 	for _, cp := range p.subscribedPairs {
 		if tickerResp.Symbol[currencyPairToMexcPair(cp)].LastPrice != 0 {
 			p.setTickerPair(cp.String(), tickerResp.Symbol[currencyPairToMexcPair(cp)])
-			telemetry.IncrCounter(
+			metrics.SafeTelemetryIncrCounter(
 				1,
 				"websocket",
 				"message",
@@ -303,7 +303,7 @@ func (p *MexcProvider) messageReceived(messageType int, bz []byte) {
 	candleErr = json.Unmarshal(bz, &candleResp)
 	if candleResp.Metadata.Close != 0 {
 		p.setCandlePair(candleResp)
-		telemetry.IncrCounter(
+		metrics.SafeTelemetryIncrCounter(
 			1,
 			"websocket",
 			"message",
@@ -414,7 +414,7 @@ func (p *MexcProvider) reconnect() error {
 
 	currencyPairs := p.subscribedPairsToSlice()
 
-	telemetry.IncrCounter(
+	metrics.SafeTelemetryIncrCounter(
 		1,
 		"websocket",
 		"reconnect",
```

### oracle/price-feeder/oracle/provider/okx.go
```diff
@@ -11,12 +11,12 @@ import (
 	"sync"
 	"time"
 
-	"github.com/cosmos/cosmos-sdk/telemetry"
 	"github.com/gorilla/websocket"
 	"github.com/rs/zerolog"
 
 	"github.com/sei-protocol/sei-chain/oracle/price-feeder/config"
 	"github.com/sei-protocol/sei-chain/oracle/price-feeder/oracle/types"
+	"github.com/sei-protocol/sei-chain/utils/metrics"
 )
 
 const (
@@ -199,7 +199,7 @@ func (p *OkxProvider) SubscribeCurrencyPairs(cps ...types.CurrencyPair) error {
 	}
 
 	p.setSubscribedPairs(cps...)
-	telemetry.IncrCounter(
+	metrics.SafeTelemetryIncrCounter(
 		float32(len(cps)),
 		"websocket",
 		"subscribe",
@@ -336,7 +336,7 @@ func (p *OkxProvider) messageReceived(messageType int, bz []byte) {
 	if tickerResp.ID.Channel == "tickers" {
 		for _, tickerPair := range tickerResp.Data {
 			p.setTickerPair(tickerPair)
-			telemetry.IncrCounter(
+			metrics.SafeTelemetryIncrCounter(
 				1,
 				"websocket",
 				"message",
@@ -353,7 +353,7 @@ func (p *OkxProvider) messageReceived(messageType int, bz []byte) {
 	if candleResp.ID.Channel == "candle1m" {
 		for _, candlePair := range candleResp.Data {
 			p.setCandlePair(candlePair, candleResp.ID.InstID)
-			telemetry.IncrCounter(
+			metrics.SafeTelemetryIncrCounter(
 				1,
 				"websocket",
 				"message",
@@ -454,7 +454,7 @@ func (p *OkxProvider) reconnect() error {
 
 	currencyPairs := p.subscribedPairsToSlice()
 
-	telemetry.IncrCounter(
+	metrics.SafeTelemetryIncrCounter(
 		1,
 		"websocket",
 		"reconnect",
```

### precompiles/bank/bank.go
```diff
@@ -6,7 +6,6 @@ import (
 	"fmt"
 	"math/big"
 
-	"github.com/cosmos/cosmos-sdk/telemetry"
 	sdk "github.com/cosmos/cosmos-sdk/types"
 	banktypes "github.com/cosmos/cosmos-sdk/x/bank/types"
 	"github.com/ethereum/go-ethereum/accounts/abi"
@@ -15,6 +14,7 @@ import (
 	"github.com/ethereum/go-ethereum/core/vm"
 	pcommon "github.com/sei-protocol/sei-chain/precompiles/common"
 	"github.com/sei-protocol/sei-chain/utils"
+	"github.com/sei-protocol/sei-chain/utils/metrics"
 	"github.com/tendermint/tendermint/libs/log"
 )
 
@@ -223,7 +223,7 @@ func (p PrecompileExecutor) sendNative(ctx sdk.Context, method *abi.Method, args
 	}
 	accExists := p.accountKeeper.HasAccount(ctx, receiverSeiAddr)
 	if !accExists {
-		defer telemetry.IncrCounter(1, "new", "account")
+		defer metrics.SafeTelemetryIncrCounter(1, "new", "account")
 		p.accountKeeper.SetAccount(ctx, p.accountKeeper.NewAccountWithAddress(ctx, receiverSeiAddr))
 	}
 
```
