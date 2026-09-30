# [?] Fix pool oob fees table mobile layout

## Summary
Severity: Unknown
Chain: Bitcoin
Component: mempool/mempool
Published: 2024-03-17
Source: https://github.com/mempool/mempool/commit/a8fa7dcb2a5e320a309e6a8b52d6802c279b2553
Type: security-commit

## Details
Fix pool oob fees table mobile layout

## Patch
### frontend/src/app/components/pool/pool.component.html
```diff
@@ -140,13 +140,13 @@ <h1 class="m-0 pt-1 pt-md-0">{{ poolStats.pool.name }}</h1>
                   <table class="table table-xs table-data">
                     <thead>
                       <tr>
-                        <th scope="col" class="data-title text-center" style="width: 33%" i18n="1w">Out-of-band Fees (1w)</th>
-                        <th scope="col" class="data-title text-center" style="width: 33%" i18n="1m">1m</th>
-                        <th scope="col" class="data-title text-center" style="width: 33%" i18n="all">All</th>
+                        <th scope="col" class="data-title clip text-center" style="width: 33%" i18n="1w">Out-of-band Fees (1w)</th>
+                        <th scope="col" class="data-title clip text-center" style="width: 33%" i18n="1m">1m</th>
+                        <th scope="col" class="data-title clip text-center" style="width: 33%" i18n="all">All</th>
                       </tr>
                     </thead>
                     <tbody>
-                      <td *ngFor="let total of oob" class="text-center"><app-amount [satoshis]="total.cost"></app-amount></td>
+                      <td *ngFor="let total of oob" class="text-center clip"><app-amount [satoshis]="total.cost" [digitsInfo]="isMobile() ? '1.2-4' : '1.8-8'"></app-amount></td>
                     </tbody>
                   </table>
                 </td>
```
