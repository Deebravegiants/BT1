# [?] sdk: phoenix subscriber overflow fix 2 (#778)

## Summary
Severity: Unknown
Chain: Solana
Component: velocity-exchange/protocol-v2
Published: 2023-12-18
Source: https://github.com/velocity-exchange/protocol-v2/commit/9da327eebc536f89c07e8842d1c0c7753c12699a
Type: security-commit

## Details
sdk: phoenix subscriber overflow fix 2 (#778)

* Pull the data for lot and tick sizes

* naming

## Patch
### sdk/examples/phoenix.ts
```diff
@@ -1,5 +1,5 @@
 import { Connection, PublicKey } from '@solana/web3.js';
-import { PRICE_PRECISION, PhoenixSubscriber } from '../src';
+import { BASE_PRECISION, PRICE_PRECISION, PhoenixSubscriber } from '../src';
 import { PROGRAM_ID } from '@ellipsis-labs/phoenix-sdk';
 
 export async function listenToBook(): Promise<void> {
@@ -19,9 +19,16 @@ export async function listenToBook(): Promise<void> {
 	await phoenixSubscriber.subscribe();
 
 	for (let i = 0; i < 10; i++) {
-		const bid = phoenixSubscriber.getBestBid().toNumber() / PRICE_PRECISION;
-		const ask = phoenixSubscriber.getBestAsk().toNumber() / PRICE_PRECISION;
-		console.log(`iter ${i}:`, bid.toFixed(3), '@', ask.toFixed(3));
+		const bids = phoenixSubscriber.getL2Levels("bids");
+		const asks = phoenixSubscriber.getL2Levels("asks");
+		console.log("bids");
+		for (const bid of bids) {
+			console.log(bid.price.toNumber() / PRICE_PRECISION.toNumber(), bid.size.toNumber() / BASE_PRECISION.toNumber());
+		}
+		console.log("asks");
+		for (const ask of asks) {
+			console.log(ask.price.toNumber() / PRICE_PRECISION.toNumber(), ask.size.toNumber() / BASE_PRECISION.toNumber());
+		}
 		await new Promise((r) => setTimeout(r, 2000));
 	}
 
```

### sdk/src/phoenix/phoenixSubscriber.ts
```diff
@@ -6,6 +6,7 @@ import {
 	toNum,
 	getMarketUiLadder,
 	Market,
+	getMarketLadder,
 } from '@ellipsis-labs/phoenix-sdk';
 import { PRICE_PRECISION } from '../constants/numericConstants';
 import { BN } from '@coral-xyz/anchor';
@@ -163,24 +164,29 @@ export class PhoenixSubscriber implements L2OrderBookGenerator {
 	}
 
 	*getL2Levels(side: 'bids' | 'asks'): Generator<L2Level> {
-		const basePrecision = Math.pow(
-			10,
-			this.market.data.header.baseParams.decimals
+		const tickSize = this.market.data.header
+			.tickSizeInQuoteAtomsPerBaseUnit as BN;
+		const baseLotsToRawBaseUnits = this.market.baseLotsToRawBaseUnits(1);
+
+		const basePrecision = new BN(
+			Math.pow(10, this.market.data.header.baseParams.decimals) *
+				baseLotsToRawBaseUnits
 		);
-		const pricePrecision = PRICE_PRECISION.toNumber();
 
-		const ladder = getMarketUiLadder(
+		const pricePrecision = PRICE_PRECISION.div(tickSize as BN);
+
+		const ladder = getMarketLadder(
 			this.market,
 			this.lastSlot,
 			this.lastUnixTimestamp,
 			20
 		);
 
 		for (let i = 0; i < ladder[side].length; i++) {
-			const { price, quantity } = ladder[side][i];
-			const size = new BN(quantity).mul(new BN(basePrecision));
+			const { priceInTicks, sizeInBaseLots } = ladder[side][i];
+			const size = sizeInBaseLots.mul(basePrecision);
 			yield {
-				price: new BN(price).mul(new BN(pricePrecision)),
+				price: priceInTicks.mul(new BN(pricePrecision)),
 				size,
 				sources: {
 					phoenix: size,
```
