# [?] Fix pizza tracker crash on unseen transaction

## Summary
Severity: Unknown
Chain: Bitcoin
Component: mempool/mempool
Published: 2024-08-02
Source: https://github.com/mempool/mempool/commit/e378df4158390319e88fb7076fb04e4d82028fed
Type: security-commit

## Details
Fix pizza tracker crash on unseen transaction

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
