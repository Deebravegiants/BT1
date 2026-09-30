# [?] Fix overflow on transaction page

## Summary
Severity: Unknown
Chain: Bitcoin
Component: mempool/mempool
Published: 2023-11-29
Source: https://github.com/mempool/mempool/commit/c5ce3167f39fc40834a0743f10de56398826577e
Type: security-commit

## Details
Fix overflow on transaction page

## Patch
### frontend/src/app/components/transaction/transaction.component.html
```diff
@@ -519,7 +519,7 @@ <h3>{{ error.error }}</h3>
           <div class="effective-fee-container">
             <app-fee-rate [fee]="tx.effectiveFeePerVsize"></app-fee-rate>
             <ng-template [ngIf]="tx?.status?.confirmed">
-              <app-tx-fee-rating class="ml-2 mr-2" *ngIf="tx.fee || tx.effectiveFeePerVsize" [tx]="tx"></app-tx-fee-rating>
+              <app-tx-fee-rating class="ml-2 mr-2 effective-fee-rating" *ngIf="tx.fee || tx.effectiveFeePerVsize" [tx]="tx"></app-tx-fee-rating>
             </ng-template>
           </div>
           <button *ngIf="cpfpInfo.bestDescendant || cpfpInfo.descendants?.length || cpfpInfo.ancestors?.length" type="button" class="btn btn-outline-info btn-sm btn-small-height float-right" (click)="showCpfpDetails = !showCpfpDetails">CPFP <fa-icon [icon]="['fas', 'info-circle']" [fixedWidth]="true"></fa-icon></button>
```

### frontend/src/app/components/transaction/transaction.component.scss
```diff
@@ -152,6 +152,16 @@
 	@media (min-width: 768px){
 		display: inline-block;
 	}
+  @media (max-width: 425px){
+		display: flex;
+    flex-direction: column;
+	}
+}
+
+.effective-fee-rating {
+  @media (max-width: 767px){
+    margin-right: 0px !important;
+  }
 }
 
 .title {
```
