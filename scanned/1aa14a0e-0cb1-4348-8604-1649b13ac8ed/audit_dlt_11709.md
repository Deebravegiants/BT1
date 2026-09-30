# [?] Merge pull request #6585 from mempool/rodribp/fix-goggles-overflow

## Summary
Severity: Unknown
Chain: Bitcoin
Component: mempool/mempool
Published: 2026-07-05
Source: https://github.com/mempool/mempool/commit/8429948d2c90b2a2759ccc3bbbf9a283af5b6911
Type: security-commit

## Details
Merge pull request #6585 from mempool/rodribp/fix-goggles-overflow

fix: goggles overflow on Y

## Patch
### frontend/src/app/components/block-filters/block-filters.component.html
```diff
@@ -6,7 +6,7 @@
     <button class="menu-toggle" (click)="menuOpen = !menuOpen" title="Mempool Goggles&reg;">
       <app-svg-images name="goggles" width="100%" height="100%"></app-svg-images>
     </button>
-    <div class="active-tags">
+    <div class="active-tags" [class.menu-open]="menuOpen">
       <ng-container *ngFor="let filter of activeFilters;">
         <button class="btn filter-tag selected" (click)="toggleFilter(filter)">{{ filters[filter].label }}</button>
       </ng-container>
```

### frontend/src/app/components/block-filters/block-filters.component.scss
```diff
@@ -18,6 +18,41 @@
     flex-wrap: wrap;
     row-gap: 0.25em;
     margin-left: 0.5em;
+    width: 100%;
+
+    &.menu-open {
+      white-space: nowrap;
+      flex-wrap: nowrap;
+      overflow-x: auto;
+      -ms-overflow-style: none;
+      scrollbar-width: none;
+      margin-right: 0.5em;
+
+      &::-webkit-scrollbar {
+        display: none;
+      }
+
+      -webkit-mask-image: linear-gradient(
+        to right,
+        transparent 0,
+        #000 var(--fade-l),
+        #000 calc(100% - var(--fade-r)),
+        transparent 100%
+      );
+
+      mask-image: linear-gradient(
+        to right,
+        transparent 0,
+        #000 var(--fade-l),
+        #000 calc(100% - var(--fade-r)),
+        transparent 100%
+      );
+
+      animation: goggles-fade-l linear both, goggles-fade-r linear both;
+      animation-timeline: scroll(self inline);
+      animation-range:0 1.5em, 0 100%;
+      animation-duration: 1ms;
+    }
   }
 
   .info-badges {
@@ -217,4 +252,27 @@
       font-size: 0.5em;
     }
   }
-}
\ No newline at end of file
+}
+
+@property --fade-l {
+  syntax: "<length>";
+  inherits: false;
+  initial-value: 0px;
+}
+
+@property --fade-r {
+  syntax: "<length>";
+  inherits: false;
+  initial-value: 0px;
+}
+
+@keyframes goggles-fade-l {
+  to {
+    --fade-l: 1em;
+  }
+}
+@keyframes goggles-fade-r {
+  from {
+    --fade-r: 1em;
+  }
+}
```
