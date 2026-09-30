# [?] Fix search bar result overflow

## Summary
Severity: Unknown
Chain: Bitcoin
Component: mempool/mempool
Published: 2024-01-22
Source: https://github.com/mempool/mempool/commit/0663cc2cfa21088de54da3cb5eedc77c6916391b
Type: security-commit

## Details
Fix search bar result overflow

## Patch
### frontend/src/app/components/search-form/search-form.component.scss
```diff
@@ -1,15 +1,11 @@
 :host ::ng-deep {
   .dropdown-item {
     white-space: nowrap;
-    width: calc(100% - 34px);
   }
   .dropdown-menu {
     width: calc(100% - 34px);
   }
   @media (min-width: 768px) {
-    .dropdown-item {
-      width: 410px;
-    }
     .dropdown-menu {
       width: 410px;
     }
```

### frontend/src/app/components/search-form/search-results/search-results.component.html
```diff
@@ -26,7 +26,7 @@
   <ng-template [ngIf]="results.address">
     <div class="card-title" i18n="search.bitcoin-address">Bitcoin Address</div>
     <button (click)="clickItem(0)" [class.active]="0 === activeIdx" type="button" role="option" class="dropdown-item">
-      <ng-container *ngTemplateOutlet="goTo; context: { $implicit: results.searchText | shortenString : isMobile ? 20 : 30 }"></ng-container>
+      <ng-container *ngTemplateOutlet="goTo; context: { $implicit: results.searchText | shortenString : isMobile ? 17 : 30 }"></ng-container>
     </button>
   </ng-template>
   <ng-template [ngIf]="results.blockHash">
@@ -39,7 +39,7 @@
     <div class="card-title danger" i18n="search.other-networks">Other Network Address</div>
     <ng-template ngFor [ngForOf]="results.otherNetworks" let-otherNetwork let-i="index">
       <button (click)="clickItem(results.hashQuickMatch + i)" [class.active]="(results.hashQuickMatch + i) === activeIdx" [class.inactive]="!otherNetwork.isNetworkAvailable" type="button" role="option" class="dropdown-item">
-        <ng-container *ngTemplateOutlet="goTo; context: { $implicit: otherNetwork.address| shortenString : isMobile ? 20 : 25 }"></ng-container>&nbsp;<b>({{ otherNetwork.network.charAt(0).toUpperCase() + otherNetwork.network.slice(1) }})</b>
+        <ng-container *ngTemplateOutlet="goTo; context: { $implicit: otherNetwork.address| shortenString : isMobile ? 12 : 20 }"></ng-container>&nbsp;<b>({{ otherNetwork.network.charAt(0).toUpperCase() + otherNetwork.network.slice(1) }})</b>
       </button>
     </ng-template>
   </ng-template>
```

### frontend/src/app/components/search-form/search-results/search-results.component.ts
```diff
@@ -10,7 +10,7 @@ export class SearchResultsComponent implements OnChanges {
   @Input() results: any = {};
   @Output() selectedResult = new EventEmitter();
 
-  isMobile = (window.innerWidth <= 767.98);
+  isMobile = (window.innerWidth <= 1150);
   resultsFlattened = [];
   activeIdx = 0;
   focusFirst = true;
```
