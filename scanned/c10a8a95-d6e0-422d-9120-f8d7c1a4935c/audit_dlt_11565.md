# [?] fix race condition

## Summary
Severity: Unknown
Chain: Solana
Component: velocity-exchange/protocol-v2
Published: 2023-11-08
Source: https://github.com/velocity-exchange/protocol-v2/commit/be22d96f0ac701c996ed101b99f40a2f6cdf75bf
Type: security-commit

## Details
fix race condition

## Patch
### sdk/src/accounts/webSocketAccountSubscriber.ts
```diff
@@ -14,6 +14,7 @@ export class WebSocketAccountSubscriber<T> implements AccountSubscriber<T> {
 	onChange: (data: T) => void;
 	listenerId?: number;
 	resubTimeoutMs?: number;
+	isUnsubscribing = false;
 	timeoutId?: NodeJS.Timeout;
 
 	receivingData: boolean;
@@ -34,7 +35,7 @@ export class WebSocketAccountSubscriber<T> implements AccountSubscriber<T> {
 	}
 
 	async subscribe(onChange: (data: T) => void): Promise<void> {
-		if (this.listenerId) {
+		if (this.listenerId || this.isUnsubscribing) {
 			return;
 		}
 
@@ -80,6 +81,11 @@ export class WebSocketAccountSubscriber<T> implements AccountSubscriber<T> {
 			throw new Error('onChange callback function must be set');
 		}
 		this.timeoutId = setTimeout(async () => {
+			if (this.isUnsubscribing) {
+				// If we are in the process of unsubscribing, do not attempt to resubscribe
+				return;
+			}
+
 			if (this.receivingData) {
 				console.log(
 					`No ws data from ${this.accountName} in ${this.resubTimeoutMs}ms, resubscribing`
@@ -154,12 +160,17 @@ export class WebSocketAccountSubscriber<T> implements AccountSubscriber<T> {
 	}
 
 	unsubscribe(): Promise<void> {
+		this.isUnsubscribing = true;
+		clearTimeout(this.timeoutId);
+		this.timeoutId = undefined;
+
 		if (this.listenerId) {
 			const promise =
 				this.program.provider.connection.removeAccountChangeListener(
 					this.listenerId
 				);
 			this.listenerId = undefined;
+			this.isUnsubscribing = false;
 			return promise;
 		}
 	}
```

### sdk/src/accounts/webSocketProgramAccountSubscriber.ts
```diff
@@ -21,6 +21,7 @@ export class WebSocketProgramAccountSubscriber<T>
 	onChange: (accountId: PublicKey, data: T, context: Context) => void;
 	listenerId?: number;
 	resubTimeoutMs?: number;
+	isUnsubscribing = false;
 	timeoutId?: NodeJS.Timeout;
 	options: { filters: MemcmpFilter[]; commitment?: Commitment };
 
@@ -48,7 +49,7 @@ export class WebSocketProgramAccountSubscriber<T>
 	async subscribe(
 		onChange: (accountId: PublicKey, data: T, context: Context) => void
 	): Promise<void> {
-		if (this.listenerId) {
+		if (this.listenerId || this.isUnsubscribing) {
 			return;
 		}
 
@@ -81,6 +82,11 @@ export class WebSocketProgramAccountSubscriber<T>
 			throw new Error('onChange callback function must be set');
 		}
 		this.timeoutId = setTimeout(async () => {
+			if (this.isUnsubscribing) {
+				// If we are in the process of unsubscribing, do not attempt to resubscribe
+				return;
+			}
+
 			if (this.receivingData) {
 				console.log(
 					`No ws data from ${this.subscriptionName} in ${this.resubTimeoutMs}ms, resubscribing`
@@ -140,12 +146,17 @@ export class WebSocketProgramAccountSubscriber<T>
 	}
 
 	unsubscribe(): Promise<void> {
+		this.isUnsubscribing = true;
+		clearTimeout(this.timeoutId);
+		this.timeoutId = undefined;
+
 		if (this.listenerId) {
 			const promise =
 				this.program.provider.connection.removeAccountChangeListener(
 					this.listenerId
 				);
 			this.listenerId = undefined;
+			this.isUnsubscribing = false;
 			return promise;
 		}
 	}
```
