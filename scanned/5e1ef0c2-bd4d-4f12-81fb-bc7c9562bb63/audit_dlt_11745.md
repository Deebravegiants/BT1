# [?] Add pagination to Lightning nodes list and fix overflow

## Summary
Severity: Unknown
Chain: Bitcoin
Component: mempool/mempool
Published: 2024-02-19
Source: https://github.com/mempool/mempool/commit/17697e669a599508c54ea0ad7ebb6f0111304520
Type: security-commit

## Details
Add pagination to Lightning nodes list and fix overflow

## Patch
### frontend/src/app/lightning/nodes-per-country/nodes-per-country.component.html
```diff
@@ -64,8 +64,8 @@ <h1>
         <th class="channels text-right" i18n="lightning.channels">Channels</th>
         <th class="city text-right" i18n="lightning.location">Location</th>
       </thead>
-      <tbody *ngIf="nodes$ | async as countryNodes; else skeleton">
-        <tr *ngFor="let node of countryNodes.nodes; let i= index; trackBy: trackByPublicKey">
+      <tbody *ngIf="nodesPagination$ | async as countryNodes; else skeleton">
+        <tr *ngFor="let node of countryNodes; let i= index; trackBy: trackByPublicKey">
           <td class="alias text-left text-truncate">
             <a [routerLink]="['/lightning/node/' | relativeUrl, node.public_key]">{{ node.alias }}</a>
           </td>
@@ -116,5 +116,10 @@ <h1>
       </ng-template>
 
     </table>
+
+    <ngb-pagination *ngIf="nodes$ | async as countryNodes" class="pagination-container float-right mt-2" [class]="isLoading ? 'disabled' : ''"
+        [collectionSize]="countryNodes.nodes.length" [rotate]="true" [maxSize]="maxSize" [pageSize]="pageSize" [(page)]="page"
+        (pageChange)="pageChange(page)" [boundaryLinks]="true" [ellipses]="false">
+      </ngb-pagination>
   </div>
 </div>
```

### frontend/src/app/lightning/nodes-per-country/nodes-per-country.component.scss
```diff
@@ -22,14 +22,14 @@
 
 .timestamp-first {
   width: 20%;
-  @media (max-width: 576px) {
+  @media (max-width: 1060px) {
     display: none
   }
 }
 
 .timestamp-update {
   width: 16%;
-  @media (max-width: 576px) {
+  @media (max-width: 1060px) {
     display: none
   }
 }
@@ -50,7 +50,7 @@
 
 .city {
   max-width: 150px;
-  @media (max-width: 576px) {
+  @media (max-width: 675px) {
     display: none
   }
 }
\ No newline at end of file
```

### frontend/src/app/lightning/nodes-per-country/nodes-per-country.component.ts
```diff
@@ -1,6 +1,6 @@
 import { ChangeDetectionStrategy, Component, Input, OnInit } from '@angular/core';
 import { ActivatedRoute } from '@angular/router';
-import { map, Observable, share } from 'rxjs';
+import { BehaviorSubject, combineLatest, map, Observable, share, tap } from 'rxjs';
 import { ApiService } from '../../services/api.service';
 import { SeoService } from '../../services/seo.service';
 import { getFlagEmoji } from '../../shared/common.utils';
@@ -15,6 +15,12 @@ import { GeolocationData } from '../../shared/components/geolocation/geolocation
 export class NodesPerCountry implements OnInit {
   nodes$: Observable<any>;
   country: {name: string, flag: string};
+  nodesPagination$: Observable<any>;
+  startingIndexSubject: BehaviorSubject<number> = new BehaviorSubject(0);
+  page = 1;
+  pageSize = 15;
+  maxSize = window.innerWidth <= 767.98 ? 3 : 5;
+  isLoading = true;
 
   skeletonLines: number[] = [];
 
@@ -23,14 +29,15 @@ export class NodesPerCountry implements OnInit {
     private seoService: SeoService,
     private route: ActivatedRoute,
   ) {
-    for (let i = 0; i < 20; ++i) {
+    for (let i = 0; i < this.pageSize; ++i) {
       this.skeletonLines.push(i);
     }
   }
 
   ngOnInit(): void {
     this.nodes$ = this.apiService.getNodeForCountry$(this.route.snapshot.params.country)
       .pipe(
+        tap(() => this.isLoading = true),
         map(response => {
           this.seoService.setTitle($localize`Lightning nodes in ${response.country.en}`);
           this.seoService.setDescription($localize`:@@meta.description.lightning.nodes-country:Explore all the Lightning nodes hosted in ${response.country.en} and see an overview of each node's capacity, number of open channels, and more.`);
@@ -87,11 +94,21 @@ export class NodesPerCountry implements OnInit {
             ispCount: Object.keys(isps).length
           };
         }),
+        tap(() => this.isLoading = false),
         share()
       );
+
+    this.nodesPagination$ = combineLatest([this.nodes$, this.startingIndexSubject]).pipe(
+      map(([response, startingIndex]) => response.nodes.slice(startingIndex, startingIndex + this.pageSize))
+    );
   }
 
   trackByPublicKey(index: number, node: any): string {
     return node.public_key;
   }
+
+  pageChange(page: number): void {
+    this.startingIndexSubject.next((page - 1) * this.pageSize);
+    this.page = page;
+  }
 }
```

### frontend/src/app/lightning/nodes-per-isp/nodes-per-isp.component.html
```diff
@@ -61,8 +61,8 @@ <h1 i18n="lightning.nodes-for-isp">Lightning nodes on ISP: {{ isp?.name }}</h1>
         <th class="channels text-right" i18n="lightning.channels">Channels</th>
         <th class="city text-right" i18n="lightning.location">Location</th>
       </thead>
-      <tbody *ngIf="nodes$ | async as ispNodes; else skeleton">
-        <tr *ngFor="let node of ispNodes.nodes; let i= index; trackBy: trackByPublicKey">
+      <tbody *ngIf="nodesPagination$ | async as ispNodes; else skeleton">
+        <tr *ngFor="let node of ispNodes; let i= index; trackBy: trackByPublicKey">
           <td class="alias text-left text-truncate">
             <a [routerLink]="['/lightning/node/' | relativeUrl, node.public_key]">{{ node.alias }}</a>
           </td>
@@ -113,5 +113,10 @@ <h1 i18n="lightning.nodes-for-isp">Lightning nodes on ISP: {{ isp?.name }}</h1>
       </ng-template>
   
     </table>
+
+    <ngb-pagination *ngIf="nodes$ | async as ispNodes" class="pagination-container float-right mt-2" [class]="isLoading ? 'disabled' : ''"
+        [collectionSize]="ispNodes.nodes.length" [rotate]="true" [maxSize]="maxSize" [pageSize]="pageSize" [(page)]="page"
+        (pageChange)="pageChange(page)" [boundaryLinks]="true" [ellipses]="false">
+      </ngb-pagination>
   </div>
 </div>
```

### frontend/src/app/lightning/nodes-per-isp/nodes-per-isp.component.scss
```diff
@@ -24,15 +24,15 @@
 .timestamp-first {
   width: 20%;
 
-  @media (max-width: 576px) {
+  @media (max-width: 1060px) {
     display: none
   }
 }
 
 .timestamp-update {
   width: 16%;
 
-  @media (max-width: 576px) {
+  @media (max-width: 1060px) {
     display: none
   }
 }
@@ -56,7 +56,7 @@
 .city {
   max-width: 150px;
 
-  @media (max-width: 576px) {
+  @media (max-width: 675px) {
     display: none
   }
 }
```

### frontend/src/app/lightning/nodes-per-isp/nodes-per-isp.component.ts
```diff
@@ -1,6 +1,6 @@
 import { ChangeDetectionStrategy, Component, OnInit } from '@angular/core';
 import { ActivatedRoute } from '@angular/router';
-import { map, Observable, share } from 'rxjs';
+import { BehaviorSubject, combineLatest, map, Observable, share, tap } from 'rxjs';
 import { ApiService } from '../../services/api.service';
 import { SeoService } from '../../services/seo.service';
 import { getFlagEmoji } from '../../shared/common.utils';
@@ -15,6 +15,12 @@ import { GeolocationData } from '../../shared/components/geolocation/geolocation
 export class NodesPerISP implements OnInit {
   nodes$: Observable<any>;
   isp: {name: string, id: number};
+  nodesPagination$: Observable<any>;
+  startingIndexSubject: BehaviorSubject<number> = new BehaviorSubject(0);
+  page = 1;
+  pageSize = 15;
+  maxSize = window.innerWidth <= 767.98 ? 3 : 5;
+  isLoading = true;
 
   skeletonLines: number[] = [];
 
@@ -23,14 +29,15 @@ export class NodesPerISP implements OnInit {
     private seoService: SeoService,
     private route: ActivatedRoute,
   ) {
-    for (let i = 0; i < 20; ++i) {
+    for (let i = 0; i < this.pageSize; ++i) {
       this.skeletonLines.push(i);
     }
   }
 
   ngOnInit(): void {
     this.nodes$ = this.apiService.getNodeForISP$(this.route.snapshot.params.isp)
       .pipe(
+        tap(() => this.isLoading = true),
         map(response => {
           this.isp = {
             name: response.isp,
@@ -77,11 +84,21 @@ export class NodesPerISP implements OnInit {
             topCountry: topCountry,
           };
         }),
+        tap(() => this.isLoading = false),
         share()
       );
+
+    this.nodesPagination$ = combineLatest([this.nodes$, this.startingIndexSubject]).pipe(
+      map(([response, startingIndex]) => response.nodes.slice(startingIndex, startingIndex + this.pageSize))
+    );
   }
 
   trackByPublicKey(index: number, node: any): string {
     return node.public_key;
   }
+
+  pageChange(page: number): void {
+    this.startingIndexSubject.next((page - 1) * this.pageSize);
+    this.page = page;
+  }
 }
```
