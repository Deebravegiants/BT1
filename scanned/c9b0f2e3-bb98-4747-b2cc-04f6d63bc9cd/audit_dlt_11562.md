# [?] fix openbook race condition

## Summary
Severity: Unknown
Chain: Solana
Component: velocity-exchange/protocol-v2
Published: 2024-08-07
Source: https://github.com/velocity-exchange/protocol-v2/commit/27711ee0cc4acdee500a59e1c8ed9fb5a65d3192
Type: security-commit

## Details
fix openbook race condition

## Patch
### sdk/src/openbook/openbookV2Subscriber.ts
```diff
@@ -72,22 +72,22 @@ export class OpenbookV2Subscriber implements L2OrderBookGenerator {
 						'Market',
 						accountInfo.data
 					);
-					this.market = new Market(this.client, this.marketAddress, marketRaw);
-					await this.market.loadOrderBook();
+					const market = new Market(this.client, this.marketAddress, marketRaw);
+					await market.loadOrderBook();
+					this.market = market;
 				}
 			);
 		} else {
 			this.marketCallbackId = await this.accountLoader.addAccount(
 				this.marketAddress,
-				(buffer, _) => {
+				async (buffer, _) => {
 					const marketRaw = openbookV2Program.coder.accounts.decode(
 						'Market',
 						buffer
 					);
-					this.market = new Market(this.client, this.marketAddress, marketRaw);
-					(async () => {
-						await this.market.loadOrderBook();
-					})();
+					const market = new Market(this.client, this.marketAddress, marketRaw);
+					await market.loadOrderBook();
+					this.market = market;
 				}
 			);
 		}
```
