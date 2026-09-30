# [?] fix hide acceleration button overflow

## Summary
Severity: Unknown
Chain: Bitcoin
Component: mempool/mempool
Published: 2024-07-05
Source: https://github.com/mempool/mempool/commit/8735b6251005222754846bcee9a03e103d5ea852
Type: security-commit

## Details
fix hide acceleration button overflow

fixes #5276

## Patch
### frontend/src/app/components/transaction/transaction.component.html
```diff
@@ -128,7 +128,7 @@ <h2 class="text-left">CPFP <fa-icon [icon]="['fas', 'info-circle']" [fixedWidth]
       <div class="title float-left mb-1">
         <h2><a [href]="[ isMempoolSpaceBuild ? '/accelerator' : 'https://mempool.space/accelerator']" [target]="isMempoolSpaceBuild ? '' : 'blank'"><app-svg-images name="accelerator" [height]="isMobile ? '35px' : '45px'"></app-svg-images></a></h2>
       </div>
-      <button type="button" class="btn btn-outline-info accelerator-toggle btn-sm float-right" (click)="closeAccelerator()" i18n="accelerator.hide">Hide accelerator</button>
+      <button type="button" class="btn btn-outline-info accelerator-toggle btn-sm float-right" [class.hide-on-mobile]="hasAccelerationDetails" (click)="closeAccelerator()" i18n="accelerator.hide">Hide accelerator</button>
       <button *ngIf="hasAccelerationDetails" class="btn btn-sm btn-outline-info details-button float-right ml-2" (click)="showAccelerationDetails = !showAccelerationDetails" i18n="transaction.details|Transaction Details">Details</button>
 
       <div class="clearfix"></div>
```

### frontend/src/app/components/transaction/transaction.component.scss
```diff
@@ -167,6 +167,12 @@
 	}
 }
 
+@media (max-width: 767px){
+  .hide-on-mobile {
+    display: none;
+  }
+}
+
 .effective-fee-rating {
   @media (max-width: 767px){
     margin-right: 0px !important;
```
