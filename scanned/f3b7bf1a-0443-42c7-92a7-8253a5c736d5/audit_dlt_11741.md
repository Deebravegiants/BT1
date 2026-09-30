# [?] Fix tooltip text overflow in some languages

## Summary
Severity: Unknown
Chain: Bitcoin
Component: mempool/mempool
Published: 2024-04-18
Source: https://github.com/mempool/mempool/commit/89ef5fe33d4549e57faa815fadc706fd14be99fb
Type: security-commit

## Details
Fix tooltip text overflow in some languages

## Patch
### frontend/src/app/components/block-overview-tooltip/block-overview-tooltip.component.scss
```diff
@@ -10,7 +10,7 @@
   padding: 10px 15px;
   text-align: left;
   min-width: 340px;
-  max-width: 340px;
+  max-width: 400px;
   pointer-events: none;
   z-index: 11;
 
@@ -41,7 +41,7 @@ th, td {
   flex-wrap: wrap;
   row-gap: 0.25em;
   margin-top: 0.2em;
-  max-width: 100%;
+  max-width: 310px;
 
   .badge {
     border-radius: 0.2rem;
```

### frontend/src/app/components/block-overview-tooltip/block-overview-tooltip.component.ts
```diff
@@ -98,6 +98,6 @@ export class BlockOverviewTooltipComponent implements OnChanges {
   }
 
   getTooltipLeftPosition(): string {
-    return window.innerWidth < 392 ? '-40px' : this.tooltipPosition.x + 'px';
+    return window.innerWidth < 392 ? '-50px' : this.tooltipPosition.x + 'px';
   }
 }
```
