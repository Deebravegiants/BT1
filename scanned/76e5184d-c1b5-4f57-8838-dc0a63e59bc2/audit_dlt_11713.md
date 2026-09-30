# [?] Merge branch 'master' into fix-pools-address-overflow

## Summary
Severity: Unknown
Chain: Bitcoin
Component: mempool/mempool
Published: 2026-02-16
Source: https://github.com/mempool/mempool/commit/348b55ec7ca4b84f095b3717d637d60008cedc53
Type: security-commit

## Details
Merge branch 'master' into fix-pools-address-overflow

## Patch
### backend/src/api/mining/mining.ts
```diff
@@ -218,7 +218,7 @@ class Mining {
     const now = new Date();
 
     // Run only if:
-    // * this.lastWeeklyHashrateIndexingDate is set to null (node backend restart, reorg)
+    // * this.lastWeeklyHashrateIndexingDate is set to null (node backend restart, reorg, or re-indexing was requested after mining pools update)
     // * we started a new week (around Monday midnight)
     const runIndexing = this.lastWeeklyHashrateIndexingDate === null ||
       now.getUTCDay() === 1 && this.lastWeeklyHashrateIndexingDate !== now.getUTCDate();
@@ -334,6 +334,7 @@ class Mining {
       logger.notice(`hashrates will now be re-indexed`);
       await database.query(`TRUNCATE hashrates`);
       this.lastHashrateIndexingDate = 0;
+      this.lastWeeklyHashrateIndexingDate = null;
       this.reindexHashrateRequested = false;
     }
 
```

### contributors/most-improve123.txt
```diff
@@ -0,0 +1,3 @@
+I hereby accept the terms of the Contributor License Agreement in the CONTRIBUTING.md file of the mempool/mempool git repository as of January 25, 2022.
+
+Signed: most-improve123
```

### frontend/src/app/components/blockchain/blockchain.component.scss
```diff
@@ -113,4 +113,12 @@
   .blockchain-wrapper .blocks-wrapper {
     direction: rtl;
   }
-}
\ No newline at end of file
+}
+.blockchain-wrapper {
+  cursor: grab;
+}
+
+.blockchain-wrapper:active {
+  cursor: grabbing;
+}
+
```

### frontend/src/app/lightning/nodes-rankings-dashboard/nodes-rankings-dashboard.component.html
```diff
@@ -10,7 +10,7 @@ <h5 class="card-title d-inline" i18n="lightning.liquidity-ranking">Liquidity Ran
             <fa-icon [icon]="['fas', 'external-link-alt']" [fixedWidth]="true"
               style="vertical-align: text-top; font-size: 13px; color: var(--title-fg)"></fa-icon>
           </a>
-          <app-top-nodes-per-capacity [nodes$]="nodesRanking$" [widget]="true"></app-top-nodes-per-capacity>
+          <app-top-nodes-per-capacity [nodes$]="nodesRanking$" [statistics$]="statistics$" [widget]="true"></app-top-nodes-per-capacity>
         </div>
       </div>
     </div>
@@ -24,7 +24,7 @@ <h5 class="card-title d-inline" i18n="lightning.connectivity-ranking">Connectivi
             <fa-icon [icon]="['fas', 'external-link-alt']" [fixedWidth]="true"
               style="vertical-align: text-top; font-size: 13px; color: var(--title-fg)"></fa-icon>
           </a>
-          <app-top-nodes-per-channels [nodes$]="nodesRanking$" [widget]="true"></app-top-nodes-per-channels>
+          <app-top-nodes-per-channels [nodes$]="nodesRanking$" [statistics$]="statistics$" [widget]="true"></app-top-nodes-per-channels>
         </div>
       </div>
     </div>
```

### frontend/src/app/lightning/nodes-rankings-dashboard/nodes-rankings-dashboard.component.ts
```diff
@@ -1,6 +1,6 @@
 import { ChangeDetectionStrategy, Component, OnInit } from '@angular/core';
 import { Observable, share } from 'rxjs';
-import { INodesRanking } from '@interfaces/node-api.interface';
+import { INodesRanking, INodesStatistics } from '@interfaces/node-api.interface';
 import { SeoService } from '@app/services/seo.service';
 import { LightningApiService } from '@app/lightning/lightning-api.service';
 
@@ -13,6 +13,7 @@ import { LightningApiService } from '@app/lightning/lightning-api.service';
 })
 export class NodesRankingsDashboard implements OnInit {
   nodesRanking$: Observable<INodesRanking>;
+  statistics$: Observable<INodesStatistics>;
 
   constructor(
     private lightningApiService: LightningApiService,
@@ -23,5 +24,6 @@ export class NodesRankingsDashboard implements OnInit {
     this.seoService.setTitle($localize`Top lightning nodes`);
     this.seoService.setDescription($localize`:@@meta.description.lightning.rankings-dashboard:See the top Lightning network nodes ranked by liquidity, connectivity, and age.`);
     this.nodesRanking$ = this.lightningApiService.getNodesRanking$().pipe(share());
+    this.statistics$ = this.lightningApiService.getLatestStatistics$().pipe(share());
   }
 }
```
