# [?] fix(ui): pools address overflow and hide button on mobile (#5917)

## Summary
Severity: Unknown
Chain: Bitcoin
Component: mempool/mempool
Published: 2026-02-07
Source: https://github.com/mempool/mempool/commit/34190aa435d9792f31f38380ea48593cdfe4f7f0
Type: security-commit

## Details
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
@@ -43,9 +43,10 @@ <h1 class="m-0 pt-1 pt-md-0">{{ poolStats.pool.name }}</h1>
                   </a>
                   <div>
                     <div #collapse="ngbCollapse" [(ngbCollapse)]="gfg">
-                      <a class="addresses-data" *ngFor="let address of poolStats.pool.addresses | slice: 1"
-                        [routerLink]="['/address' | relativeUrl, address]">{{
-                        address }}<br></a>
+                     <a class="addresses-data"
+                        *ngFor="let address of poolStats.pool.addresses | slice: 1"
+                        [routerLink]="['/address' | relativeUrl, address]">
+                        <app-truncate [text]="address" [lastChars]="8"></app-truncate></a>
                     </div>
                     <button *ngIf="poolStats.pool.addresses.length >= 2" type="button"
                       class="btn btn-sm btn-primary small-button" (click)="collapse.toggle()"
@@ -65,7 +66,9 @@ <h1 class="m-0 pt-1 pt-md-0">{{ poolStats.pool.name }}</h1>
                     <button *ngIf="poolStats.pool.addresses.length >= 2" type="button"
                       class="btn btn-sm btn-primary float-right small-button mobile" (click)="collapse.toggle()"
                       [attr.aria-expanded]="!gfg" aria-controls="collapseExample">
-                      <span i18n="show-all">Show all</span> ({{ poolStats.pool.addresses.length }})
+                      <span *ngIf="gfg" i18n="show-all">Show all</span>
+                      <span *ngIf="!gfg" i18n="hide">Hide</span>
+                      ({{ poolStats.pool.addresses.length }})
                     </button>
                     <a class="addresses-data" [routerLink]="['/address' | relativeUrl, poolStats.pool.addresses[0]]">
                       {{ poolStats.pool.addresses[0] | shortenString: 30 }}
```
