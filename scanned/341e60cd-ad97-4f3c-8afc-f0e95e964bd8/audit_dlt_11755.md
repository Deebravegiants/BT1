# [?] Fixing mobile overflow

## Summary
Severity: Unknown
Chain: Bitcoin
Component: mempool/mempool
Published: 2023-11-15
Source: https://github.com/mempool/mempool/commit/86fe6a802b2bb069cd32bdb62f079fad961e90de
Type: security-commit

## Details
Fixing mobile overflow

## Patch
### frontend/src/app/shared/components/truncate/truncate.component.html
```diff
@@ -1,4 +1,5 @@
 <span class="truncate" [style.max-width]="maxWidth ? maxWidth + 'px' : null" [style.justify-content]="textAlign" [class.inline]="inline">
+  <div class="hidden">{{ text }}</div>
     <ng-container *ngIf="link">
       <a [routerLink]="link" class="truncate-link">
         <ng-container *ngIf="rtl; then rtlTruncated; else ltrTruncated;"></ng-container>
@@ -11,11 +12,10 @@
 </span>
 
 <ng-template #ltrTruncated>
-  <div class="hidden">{{ text }}</div>
+
   <span class="first">{{text.slice(0,-lastChars)}}</span><span class="last-four">{{text.slice(-lastChars)}}</span>
 </ng-template>
 
 <ng-template #rtlTruncated>
-  <div class="hidden">{{ text }}</div>
   <span class="first">{{text.slice(lastChars)}}</span><span class="last-four">{{text.slice(0,lastChars)}}</span>
 </ng-template>
\ No newline at end of file
```

### frontend/src/app/shared/components/truncate/truncate.component.scss
```diff
@@ -32,4 +32,12 @@
 .hidden { 
   color: transparent;
   position: absolute;
-}
\ No newline at end of file
+  max-width: 300px;
+  overflow: hidden;
+}
+
+@media (max-width: 567px) {
+  .hidden {
+    max-width: 150px;
+  }
+}
```
