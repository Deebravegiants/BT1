# [?] Fix crypto lib call crash with custom function

## Summary
Severity: Unknown
Chain: Bitcoin
Component: mempool/mempool
Published: 2024-07-21
Source: https://github.com/mempool/mempool/commit/743c7e8bfb6f12e3b543ac5a2231383cf1d3b73d
Type: security-commit

## Details
Fix crypto lib call crash with custom function

## Patch
### frontend/src/app/components/accelerate-checkout/accelerate-checkout.component.ts
```diff
@@ -1,7 +1,7 @@
 import { Component, OnInit, OnDestroy, Output, EventEmitter, Input, ChangeDetectorRef, SimpleChanges, HostListener } from '@angular/core';
 import { Subscription, tap, of, catchError, Observable, switchMap } from 'rxjs';
 import { ServicesApiServices } from '../../services/services-api.service';
-import { nextRoundNumber } from '../../shared/common.utils';
+import { nextRoundNumber, simpleRandomUUID } from '../../shared/common.utils';
 import { StateService } from '../../services/state.service';
 import { AudioService } from '../../services/audio.service';
 import { ETA, EtaService } from '../../services/eta.service';
@@ -130,7 +130,7 @@ export class AccelerateCheckout implements OnInit, OnDestroy {
     private authService: AuthServiceMempool,
     private enterpriseService: EnterpriseService,
   ) {
-    this.accelerationUUID = window.crypto.randomUUID();
+    this.accelerationUUID = simpleRandomUUID();
   }
 
   ngOnInit() {
```

### frontend/src/app/shared/common.utils.ts
```diff
@@ -181,4 +181,17 @@ export function uncompressDeltaChange(delta: MempoolBlockDeltaCompressed): Mempo
       acc: !!tx[3],
     }))
   };
-}
\ No newline at end of file
+}
+
+export function simpleRandomUUID(): string {
+  const hexDigits = '0123456789abcdef';
+  const uuidLengths = [8, 4, 4, 4, 12];
+  let uuid = '';
+  for (const length of uuidLengths) {
+      for (let i = 0; i < length; i++) {
+          uuid += hexDigits[Math.floor(Math.random() * 16)];
+      }
+      uuid += '-';
+  }
+  return uuid.slice(0, -1);
+}
```
