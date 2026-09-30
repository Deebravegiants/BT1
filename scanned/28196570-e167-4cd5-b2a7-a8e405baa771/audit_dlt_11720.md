# [?] fix op_return toggle overflow

## Summary
Severity: Unknown
Chain: Bitcoin
Component: mempool/mempool
Published: 2025-07-26
Source: https://github.com/mempool/mempool/commit/048a706b2516120f0d3e90978959482e766ef854
Type: security-commit

## Details
fix op_return toggle overflow

## Patch
### frontend/src/app/components/transactions-list/transactions-list.component.html
```diff
@@ -342,16 +342,20 @@
                           <button (click)="toggleOrdData(tx.txid, 'vout', vindex)" type="button" class="btn btn-sm badge badge-ord">Runestone</button>
                         } @else {
                           <a placement="bottom" style="cursor: pointer;">
-                            <span *ngIf="vout.scriptpubkey_asm !== 'OP_RETURN'" class="badge badge-secondary scriptmessage" (click)="toggleShowFullOpReturnPreview(vindex)">{{ vout.scriptpubkey_asm | hex2ascii | slice:0:200 }}</span>
-                            <ng-container *ngIf="(showDetails$ | async) === false">
-                              @if ((vout.scriptpubkey_asm | hex2ascii).length > 200) {
-                                @if (!showFullOpReturnPreview[vindex]) {
-                                  <span class="badge badge-primary" (click)="toggleShowFullOpReturnPreview(vindex)">Show more</span>
-                                } @else {
-                                  <span class="badge badge-primary" (click)="toggleShowFullOpReturnPreview(vindex)">Show less</span>
+                            @if ((vout.scriptpubkey_asm | hex2ascii).length > 200) {
+                              <span *ngIf="vout.scriptpubkey_asm !== 'OP_RETURN'" class="badge badge-secondary scriptmessage opreturn-msg" (click)="toggleShowFullOpReturnPreview(vindex)">{{ vout.scriptpubkey_asm | hex2ascii | slice:0:200 }}</span>
+                              <ng-container *ngIf="(showDetails$ | async) === false">
+                                @if ((vout.scriptpubkey_asm | hex2ascii).length > 200) {
+                                  @if (!showFullOpReturnPreview[vindex]) {
+                                    <span class="badge badge-primary" (click)="toggleShowFullOpReturnPreview(vindex)">Show more</span>
+                                  } @else {
+                                    <span class="badge badge-primary" (click)="toggleShowFullOpReturnPreview(vindex)">Show less</span>
+                                  }
                                 }
-                              }
-                            </ng-container>
+                              </ng-container>
+                            } @else {
+                              <span *ngIf="vout.scriptpubkey_asm !== 'OP_RETURN'" [ngbTooltip]="vout.scriptpubkey_asm | hex2ascii" class="badge badge-secondary scriptmessage">{{ vout.scriptpubkey_asm | hex2ascii }}</span>
+                            }
                           </a>
                         }
                       </ng-template>
```

### frontend/src/app/components/transactions-list/transactions-list.component.scss
```diff
@@ -324,3 +324,25 @@ h2 {
 		background-color: var(--primary);
 	}
 }
+
+.scriptmessage.opreturn-msg {
+	max-width: 20px;
+	@media (min-width: 476px) {
+		max-width: 110px;
+	}
+	@media (min-width: 576px) {
+		max-width: 190px;
+	}
+	@media (min-width: 768px) {
+    max-width: 330px;
+	}
+	@media (min-width: 850px) {
+    max-width: 452px;
+	}
+	@media (min-width: 992px) {
+		max-width: 120px;
+	}
+	@media (min-width: 1200px) {
+		max-width: 180px;
+	}
+}
\ No newline at end of file
```

### frontend/src/app/components/transactions-list/transactions-list.component.ts
```diff
@@ -553,9 +553,7 @@ export class TransactionsListComponent implements OnInit, OnChanges, OnDestroy {
   }
 
   toggleShowFullOpReturnPreview(voutIndex: number): void {
-    console.log('toggleShowFullOpReturnPreview', voutIndex);
     this.showFullOpReturnPreview[voutIndex] = !this.showFullOpReturnPreview[voutIndex];
-    console.log(this.showFullOpReturnPreview[voutIndex]);
   }
 
   toggleOrdData(txid: string, type: 'vin' | 'vout', index: number) {
```
