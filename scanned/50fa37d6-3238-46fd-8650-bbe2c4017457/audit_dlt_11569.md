# [?] tests: try fixing race condition in referrer.ts test

## Summary
Severity: Unknown
Chain: Solana
Component: velocity-exchange/protocol-v2
Published: 2022-08-24
Source: https://github.com/velocity-exchange/protocol-v2/commit/43210cb1793b511b3cd92f1999e37a6ff67f9ba5
Type: security-commit

## Details
tests: try fixing race condition in referrer.ts test

## Patch
### sdk/src/clearingHouse.ts
```diff
@@ -224,11 +224,13 @@ export class ClearingHouse {
 	 *	Forces the accountSubscriber to fetch account updates from rpc
 	 */
 	public async fetchAccounts(): Promise<void> {
-		await Promise.all(
-			[...this.users.values()]
-				.map((user) => user.fetchAccounts())
-				.concat(this.accountSubscriber.fetch())
-		);
+		const promises = [...this.users.values()]
+			.map((user) => user.fetchAccounts())
+			.concat(this.accountSubscriber.fetch());
+		if (this.userStats) {
+			promises.concat(this.userStats.fetchAccounts());
+		}
+		await Promise.all(promises);
 	}
 
 	public async unsubscribe(): Promise<void> {
```

### tests/referrer.ts
```diff
@@ -212,6 +212,7 @@ describe('referrer', () => {
 		assert(eventRecord.referrerReward.eq(new BN(5000)));
 		assert(eventRecord.refereeDiscount.eq(new BN(5000)));
 
+		await referrerClearingHouse.fetchAccounts();
 		const referrerStats = referrerClearingHouse.getUserStats().getAccount();
 		assert(referrerStats.totalReferrerReward.eq(new BN(5000)));
 
```
