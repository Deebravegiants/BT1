# [?] Disabling liquid test and fixing liquid overflow

## Summary
Severity: Unknown
Chain: Bitcoin
Component: mempool/mempool
Published: 2024-06-20
Source: https://github.com/mempool/mempool/commit/1219526e2dba6410a0ca65133af5a8861ef7aeb4
Type: security-commit

## Details
Disabling liquid test and fixing liquid overflow

## Patch
### frontend/cypress/e2e/liquid/liquid.spec.ts
```diff
@@ -72,20 +72,6 @@ describe('Liquid', () => {
       });
     });
 
-    it('renders unconfidential addresses correctly on mobile', () => {
-      cy.viewport('iphone-6');
-      cy.visit(`${basePath}/address/ex1qqmmjdwrlg59c8q4l75sj6wedjx57tj5grt8pat`);
-      cy.waitForSkeletonGone();
-      //TODO: Add proper IDs for these selectors
-      const firstRowSelector = '.container-xl > :nth-child(3) > div > :nth-child(1) > .table > tbody';
-      const thirdRowSelector = '.container-xl > :nth-child(3) > div > :nth-child(3)';
-      cy.get(firstRowSelector).invoke('css', 'width').then(firstRowWidth => {
-        cy.get(thirdRowSelector).invoke('css', 'width').then(thirdRowWidth => {
-          expect(parseInt(firstRowWidth)).to.be.lessThan(parseInt(thirdRowWidth));
-        });
-      });
-    });
-
     describe('peg in/peg out', () => {
       it('loads peg in addresses', () => {
         cy.visit(`${basePath}/tx/fe764f7bedfc2a37b29d9c8aef67d64a57d253a6b11c5a55555cfd5826483a58`);
```

### frontend/src/app/components/address/address.component.html
```diff
@@ -22,7 +22,7 @@ <h1 i18n="shared.address">Address</h1>
       <div class="row">
         @if (isMobile) {
           <div class="col-sm">
-            <table class="table table-borderless table-striped">
+            <table class="table table-borderless table-striped address-table">
               <tbody>
                 <ng-container *ngTemplateOutlet="balanceRow"></ng-container>
                 <ng-container *ngTemplateOutlet="pendingBalanceRow"></ng-container>
@@ -39,7 +39,7 @@ <h1 i18n="shared.address">Address</h1>
           </div>
         } @else {
           <div class="col-sm">
-            <table class="table table-borderless table-striped table-fixed">
+            <table class="table table-borderless table-striped table-fixed address-table">
               <tbody>
                 <ng-container *ngTemplateOutlet="balanceRow"></ng-container>
                 <ng-container *ngTemplateOutlet="utxoRow"></ng-container>
@@ -52,7 +52,7 @@ <h1 i18n="shared.address">Address</h1>
             </table>
           </div>
           <div class="col-sm">
-            <table class="table table-borderless table-striped table-fixed">
+            <table class="table table-borderless table-striped table-fixed address-table">
               <tbody>
                 <ng-container *ngTemplateOutlet="pendingBalanceRow"></ng-container>
                 <ng-container *ngTemplateOutlet="pendingUtxoRow"></ng-container>
```

### frontend/src/app/components/address/address.component.scss
```diff
@@ -98,13 +98,6 @@ h1 {
 .liquid-address {
   .address-table {
     table-layout: fixed;
-
-    tr td:first-child {
-      width: 170px;
-    }
-    tr td:last-child {
-      width: 80%;
-    }
   }
 }
 
```
