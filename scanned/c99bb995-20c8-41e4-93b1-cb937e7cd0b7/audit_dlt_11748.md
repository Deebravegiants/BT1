# [?] Merge pull request #4505 from natsee/fix-overflow-pool-ranking

## Summary
Severity: Unknown
Chain: Bitcoin
Component: mempool/mempool
Published: 2024-01-26
Source: https://github.com/mempool/mempool/commit/bad39923979dc0e31bf384f744789e7f17f7ba92
Type: security-commit

## Details
Merge pull request #4505 from natsee/fix-overflow-pool-ranking

Fix overflow on mining pool ranking table

## Patch
### frontend/src/app/components/pool-ranking/pool-ranking.component.html
```diff
@@ -92,7 +92,7 @@
           <th class="" i18n="mining.pool-name">Pool</th>
           <th class="" *ngIf="this.miningWindowPreference === '24h'" i18n="mining.hashrate">Hashrate</th>
           <th class="" i18n="master-page.blocks">Blocks</th>
-          <th *ngIf="auditAvailable" class="health text-right widget" i18n="latest-blocks.avg_health"
+          <th *ngIf="auditAvailable" class="health text-right widget" [ngClass]="{'health-column': this.miningWindowPreference === '24h'}" i18n="latest-blocks.avg_health"
             i18n-ngbTooltip="latest-blocks.avg_health" ngbTooltip="Avg Health" placement="bottom" #health [disableTooltip]="!isEllipsisActive(health)">Avg Health</th>
           <th *ngIf="auditAvailable" class="d-none d-sm-table-cell" i18n="mining.fees-per-block">Avg Block Fees</th>
           <th class="d-none d-lg-table-cell" i18n="mining.empty-blocks">Empty Blocks</th>
@@ -104,13 +104,13 @@
           <td class="text-right">
             <img width="25" height="25" src="{{ pool.logo }}" [alt]="pool.name + ' mining pool logo'" onError="this.src = '/resources/mining-pools/default.svg'">
           </td>
-          <td class=""><a [routerLink]="[('/mining/pool/' + pool.slug) | relativeUrl]">{{ pool.name }}</a></td>
+          <td class="pool-name"><a [routerLink]="[('/mining/pool/' + pool.slug) | relativeUrl]">{{ pool.name }}</a></td>
           <td class="" *ngIf="this.miningWindowPreference === '24h'">{{ pool.lastEstimatedHashrate }} {{
             miningStats.miningUnits.hashrateUnit }}</td>
           <td class="d-flex justify-content-center">
             {{ pool.blockCount }}<span class="d-none d-md-table-cell">&nbsp;({{ pool.share }}%)</span>
           </td>
-          <td *ngIf="auditAvailable" class="health text-right" [ngClass]="{'widget': widget, 'legacy': !indexingAvailable}">
+          <td *ngIf="auditAvailable" class="health text-right" [ngClass]="{'widget': widget, 'legacy': !indexingAvailable, 'health-column': this.miningWindowPreference === '24h'}">
             <a
               class="health-badge badge"
               [class.badge-success]="pool.avgMatchRate >= 99"
```

### frontend/src/app/components/pool-ranking/pool-ranking.component.scss
```diff
@@ -41,6 +41,18 @@
   }
 }
 
+@media (max-width: 430px) {
+  .pool-name {
+    max-width: 110px;
+    white-space: nowrap;
+    overflow: hidden;
+    text-overflow: ellipsis;
+  }
+  .health-column {
+    display: none;
+  }
+}
+
 .loadingGraphs {
   position: absolute;
   top: 50%;
```
