# [?] fix auth refresh race condition

## Summary
Severity: Unknown
Chain: Bitcoin
Component: mempool/mempool
Published: 2024-07-02
Source: https://github.com/mempool/mempool/commit/ec2ab174de4daded43f66c0a02fe138cc3c43cc4
Type: security-commit

## Details
fix auth refresh race condition

## Patch
### frontend/src/app/components/accelerate-checkout/accelerate-checkout.component.ts
```diff
@@ -120,10 +120,14 @@ export class AccelerateCheckout implements OnInit, OnDestroy {
 
   ngOnInit() {
     this.authSubscription$ = this.authService.getAuth$().subscribe((auth) => {
-      this.auth = auth;
-      this.estimate = null;
-      this.error = null;
-      this.moveToStep('summary');
+      if (this.auth?.user?.userId !== auth?.user?.userId) {
+        this.auth = auth;
+        this.estimate = null;
+        this.error = null;
+        this.moveToStep('summary');
+      } else {
+        this.auth = auth;
+      }
     });
     this.authService.refreshAuth$().subscribe();
 
```
