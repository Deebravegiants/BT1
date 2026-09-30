# [?] Merge pull request #5918 from mempool/natsoni/fix-tx-details-crash

## Summary
Severity: Unknown
Chain: Bitcoin
Component: mempool/mempool
Published: 2025-05-21
Source: https://github.com/mempool/mempool/commit/6be58dda8f6f9c2ba7b77273ae8a31ba82bd9f64
Type: security-commit

## Details
Merge pull request #5918 from mempool/natsoni/fix-tx-details-crash

Fix coinbase tx details toggle

## Patch
### frontend/src/app/components/transactions-list/transactions-list.component.html
```diff
@@ -174,7 +174,7 @@
                         <td style="text-align: left;">
                           <ng-container *ngFor="let witness of vin.witness; index as windex">
                             <p class="witness-item">
-                              <ng-container *ngIf="tx['_sigmap'][witness] as sigInfo">
+                              <ng-container *ngIf="tx['_sigmap']?.[witness] as sigInfo">
                                 <span class="sig sig-key sig-inline sighash-{{sigInfo.sig.sighash}}"
                                       [class.hovered]="selectedSig && selectedSig.txIndex === i && selectedSig.vindex === vindex && selectedSig.sig === sigInfo.sig"
                                       (mouseenter)="showSigInfo(i, vindex, sigInfo.sig)" 
@@ -195,7 +195,7 @@
                                   {{ witness }}
                                 }
                               } @else if (witness) {
-                                <ng-container *ngIf="tx['_sigmap'][witness]?.sig.sighash !== 0 && tx['_sigmap'][witness] as sigInfo; else plainSig">
+                                <ng-container *ngIf="tx['_sigmap']?.[witness]?.sig.sighash !== 0 && tx['_sigmap']?.[witness] as sigInfo; else plainSig">
                                   <span class="witness">
                                     {{witness.slice(0, -2)}}<span class="sig sighash-{{sigInfo.sig.sighash}}" 
                                           [class.hovered]="selectedSig && selectedSig.txIndex === i && selectedSig.vindex === vindex && selectedSig.sig === sigInfo.sig"
```

### frontend/src/app/shared/components/asm/asm.component.html
```diff
@@ -2,7 +2,7 @@
   @for (instruction of instructions; track instruction.instruction) {
     <span [class]='opcodeStyles.get(instruction.instruction)'>OP_{{instruction.instruction}}</span>
     @for (arg of instruction.args; track arg) {
-      <ng-container *ngIf="annotations.signatures[arg] as sigInfo; else plainArg">
+      <ng-container *ngIf="annotations.signatures?.[arg] as sigInfo; else plainArg">
         <span class="sig sig-key sig-inline sighash-{{sigInfo.sig.sighash}}"
               [class.hovered]="annotations.selectedSig && annotations.selectedSig === sigInfo.sig"
               (mouseenter)="doShowSigInfo(sigInfo.sig)"
```
