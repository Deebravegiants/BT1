# [?] Merge pull request #6274 from OscarG673/fix-pools-address-overflow

## Summary
Severity: Unknown
Chain: Bitcoin
Component: mempool/mempool
Published: 2026-02-16
Source: https://github.com/mempool/mempool/commit/5ae7cdc385b43a47b5f2a628072ad49de9acf6e6
Type: security-commit

## Details
Merge pull request #6274 from OscarG673/fix-pools-address-overflow

fix(ui): pools address overflow and hide button on mobile (#5917)

## Patch
### contributors/OscarG673
```diff
@@ -0,0 +1,3 @@
+I hereby accept the terms of the Contributor License Agreement in the CONTRIBUTING.md file of the mempool/mempool git repository as of February 7, 2026.
+
+Signed: OscarG673
```

### frontend/src/app/components/pool/pool.component.html
```diff
@@ -38,14 +38,19 @@ <h1 class="m-0 pt-1 pt-md-0">{{ poolStats.pool.name }}</h1>
               <tr *ngIf="!isMobile()" class="taller-row">
                 <td class="label addresses" i18n="mining.addresses">Addresses</td>
                 <td *ngIf="poolStats.pool.addresses.length else nodata" style="padding-top: 25px">
-                  <a  class="addresses-data" [routerLink]="['/address' | relativeUrl, poolStats.pool.addresses[0]]">
-                    {{ poolStats.pool.addresses[0] }}
-                  </a>
+                  <app-truncate
+                  class="addresses-data"
+                  [text]="poolStats.pool.addresses[0]"
+                  [lastChars]="8"
+                  [link]="['/address' | relativeUrl, poolStats.pool.addresses[0]]"
+                  [external]="true">
+                </app-truncate>
                   <div>
                     <div #collapse="ngbCollapse" [(ngbCollapse)]="gfg">
-                      <a class="addresses-data" *ngFor="let address of poolStats.pool.addresses | slice: 1"
-                        [routerLink]="['/address' | relativeUrl, address]">{{
-                        address }}<br></a>
+                      <app-truncate class="addresses-data" *ngFor="let address of poolStats.pool.addresses | slice: 1"
+                      [link]="['/address' | relativeUrl, address]"
+                      [text]="address" [lastChars]="8">
+                    </app-truncate>
                     </div>
                     <button *ngIf="poolStats.pool.addresses.length >= 2" type="button"
                       class="btn btn-sm btn-primary small-button" (click)="collapse.toggle()"
@@ -65,15 +70,21 @@ <h1 class="m-0 pt-1 pt-md-0">{{ poolStats.pool.name }}</h1>
                     <button *ngIf="poolStats.pool.addresses.length >= 2" type="button"
                       class="btn btn-sm btn-primary float-right small-button mobile" (click)="collapse.toggle()"
                       [attr.aria-expanded]="!gfg" aria-controls="collapseExample">
-                      <span i18n="show-all">Show all</span> ({{ poolStats.pool.addresses.length }})
+                      <span *ngIf="gfg"><span i18n="show-all">Show all</span> ({{ poolStats.pool.addresses.length }})</span>
+                      <span *ngIf="!gfg" i18n="hide">Hide</span>
                     </button>
-                    <a class="addresses-data" [routerLink]="['/address' | relativeUrl, poolStats.pool.addresses[0]]">
-                      {{ poolStats.pool.addresses[0] | shortenString: 30 }}
-                    </a>
+                    <app-truncate
+                      class="addresses-data"
+                      [text]="poolStats.pool.addresses[0]"
+                      [lastChars]="8"
+                      [link]="['/address' | relativeUrl, poolStats.pool.addresses[0]]"
+                      [external]="true">
+                    </app-truncate>
                     <div #collapse="ngbCollapse" [(ngbCollapse)]="gfg" style="width: 100%">
-                      <a class="addresses-data" *ngFor="let address of poolStats.pool.addresses | slice: 1"
-                        [routerLink]="['/address' | relativeUrl, address]">{{
-                        address | shortenString: 30 }}<br></a>
+                      <app-truncate class="addresses-data" *ngFor="let address of poolStats.pool.addresses | slice: 1"
+                        [link]="['/address' | relativeUrl, address]"
+                        [text]="address" [lastChars]="8">
+                      </app-truncate>
                     </div>
                   </div>
                 </td>
```
