# [?] Fix input/output overflow in transaction list

## Summary
Severity: Unknown
Chain: Bitcoin
Component: mempool/mempool
Published: 2024-10-17
Source: https://github.com/mempool/mempool/commit/7a8ae7c9a6ad352937e1958e61ecf3e611cc2444
Type: security-commit

## Details
Fix input/output overflow in transaction list

## Patch
### frontend/src/app/components/transactions-list/transactions-list.component.html
```diff
@@ -81,7 +81,7 @@
                     </ng-container>
                   </div>
                 </td>
-                <td class="text-right nowrap amount" [class]="{large: vin?.prevout?.value > 1000000000 || vin.isInscription}">
+                <td class="text-right nowrap amount" [class]="{large: tx.largeInput}">
                   <button *ngIf="vin.isInscription" (click)="toggleOrdData(tx.txid, 'vin', vindex)" type="button" class="btn btn-sm badge badge-ord primary" style="margin-right: 10px;">Inscription</button>
                   <ng-template [ngIf]="vin.prevout && vin.prevout.asset && vin.prevout.asset !== nativeAssetId" [ngIfElse]="defaultOutput">
                     <div *ngIf="assetsMinimal && assetsMinimal[vin.prevout.asset] else assetVinNotFound">
@@ -257,7 +257,7 @@
                     </ng-template>
                   </ng-template>
                 </td>
-                <td class="text-right nowrap amount" [class]="{large: vout?.value > 1000000000}">
+                <td class="text-right nowrap amount" [class]="{large: tx.largeOutput}">
                   <ng-template [ngIf]="vout.asset && vout.asset !== nativeAssetId" [ngIfElse]="defaultOutput">
                     <div *ngIf="assetsMinimal && assetsMinimal[vout.asset] else assetNotFound">
                       <ng-container *ngTemplateOutlet="assetBox; context:{ $implicit: vout }"></ng-container>
```

### frontend/src/app/components/transactions-list/transactions-list.component.ts
```diff
@@ -252,6 +252,7 @@ export class TransactionsListComponent implements OnInit, OnChanges {
               const hasAnnex = tx.vin[i].witness?.[tx.vin[i].witness.length - 1].startsWith('50');
               if (tx.vin[i].witness.length > (hasAnnex ? 2 : 1) && tx.vin[i].witness[tx.vin[i].witness.length - (hasAnnex ? 3 : 2)].includes('0063036f7264')) {
                 tx.vin[i].isInscription = true;
+                tx.largeInput = true;
               }
             }
           }
@@ -262,6 +263,9 @@ export class TransactionsListComponent implements OnInit, OnChanges {
             }
           }
         }
+
+        tx.largeInput = tx.largeInput || tx.vin.some(vin => (vin?.prevout?.value > 1000000000));
+        tx.largeOutput = tx.vout.some(vout => (vout?.value > 1000000000));
       });
 
       if (this.blockTime && this.transactions?.length && this.currency) {
```

### frontend/src/app/interfaces/electrs.interface.ts
```diff
@@ -32,6 +32,8 @@ export interface Transaction {
   price?: Price;
   sigops?: number;
   flags?: bigint;
+  largeInput?: boolean;
+  largeOutput?: boolean;
 }
 
 export interface TransactionChannels {
```
