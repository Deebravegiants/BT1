# [?] Merge pull request #5408 from mempool/natsoni/pizza-tracker-fix-crash

## Summary
Severity: Unknown
Chain: Bitcoin
Component: mempool/mempool
Published: 2024-08-04
Source: https://github.com/mempool/mempool/commit/5ea44f2e7d79532df809d398a0c9a58a5d368ac6
Type: security-commit

## Details
Merge pull request #5408 from mempool/natsoni/pizza-tracker-fix-crash

Pizza tracker: handle transaction not yet in mempool

## Patch
### frontend/src/app/components/tracker/tracker.component.html
```diff
@@ -118,7 +118,7 @@
         </div>
         <span class="explainer">&nbsp;</span>
       } @else {
-        @if (!tx.status?.confirmed && showAccelerationSummary) {
+        @if (tx && !tx.status?.confirmed && showAccelerationSummary) {
           <ng-container *ngIf="(ETA$ | async) as eta;">
             <app-accelerate-checkout
               *ngIf="(da$ | async) as da;"
@@ -135,7 +135,7 @@
             ></app-accelerate-checkout>
           </ng-container>
         }
-        <div class="status-panel d-flex flex-column h-100 w-100 justify-content-center align-items-center" [class.small-status]="!tx.status?.confirmed && showAccelerationSummary">
+        <div class="status-panel d-flex flex-column h-100 w-100 justify-content-center align-items-center" [class.small-status]="tx && !tx.status?.confirmed && showAccelerationSummary">
           @if (tx?.acceleration && !tx.status?.confirmed) {
             <div class="progress-icon">
               <fa-icon [icon]="['fas', 'wand-magic-sparkles']" [fixedWidth]="true"></fa-icon>
@@ -186,7 +186,7 @@
     </div>
 
     <div class="footer-link"
-      [routerLink]="['/tx' | relativeUrl, tx?.txid]"
+      [routerLink]="['/tx' | relativeUrl, tx?.txid || txId]"
       [queryParams]="{ mode: 'details' }"
       queryParamsHandling="merge"
     >
```
