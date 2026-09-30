# [?] Fix Liquid crash

## Summary
Severity: Unknown
Chain: Bitcoin
Component: mempool/mempool
Published: 2024-04-01
Source: https://github.com/mempool/mempool/commit/061abaa14879784298011e5d9318ccbf1a3db45c
Type: security-commit

## Details
Fix Liquid crash

## Patch
### frontend/src/app/components/mempool-blocks/mempool-blocks.component.html
```diff
@@ -20,10 +20,12 @@
                 -
                 <app-fee-rate [fee]="projectedBlock.feeRange[projectedBlock.feeRange.length - 1]" rounding="1.0-0" unitClass=""></app-fee-rate>
               </div>
-              <div *ngIf="showMiningInfo" class="block-size">
+              <div *ngIf="showMiningInfo$ | async; else noMiningInfo" class="block-size">
                 <app-amount [attr.data-cy]="'mempool-block-' + i + '-total-fees'" [satoshis]="projectedBlock.totalFees" digitsInfo="1.2-3" [noFiat]="true"></app-amount>
               </div>
-              <div *ngIf="!showMiningInfo" class="block-size" [innerHTML]="'&lrm;' + (projectedBlock.blockSize | bytes: 2)"></div>
+              <ng-template #noMiningInfo>
+                <div class="block-size" [innerHTML]="'&lrm;' + (projectedBlock.blockSize | bytes: 2)"></div>
+              </ng-template>
               <div [attr.data-cy]="'mempool-block-' + i + '-transaction-count'" class="transaction-count">
                 <ng-container *ngTemplateOutlet="projectedBlock.nTx === 1 ? transactionsSingular : transactionsPlural; context: {$implicit: projectedBlock.nTx | number}"></ng-container>
                 <ng-template #transactionsSingular let-i i18n="shared.transaction-count.singular">{{ i }} transaction</ng-template>
```

### frontend/src/app/components/mempool-blocks/mempool-blocks.component.ts
```diff
@@ -1,5 +1,5 @@
 import { Component, OnInit, OnDestroy, ChangeDetectionStrategy, ChangeDetectorRef, HostListener, Input, OnChanges, SimpleChanges, Output, EventEmitter } from '@angular/core';
-import { Subscription, Observable, of, combineLatest } from 'rxjs';
+import { Subscription, Observable, of, combineLatest, BehaviorSubject } from 'rxjs';
 import { MempoolBlock } from '../../interfaces/websocket.interface';
 import { StateService } from '../../services/state.service';
 import { Router } from '@angular/router';
@@ -42,6 +42,7 @@ export class MempoolBlocksComponent implements OnInit, OnChanges, OnDestroy {
   mempoolBlocks$: Observable<MempoolBlock[]>;
   difficultyAdjustments$: Observable<DifficultyAdjustment>;
   loadingBlocks$: Observable<boolean>;
+  showMiningInfo$: BehaviorSubject<boolean> = new BehaviorSubject<boolean>(false);
   blocksSubscription: Subscription;
 
   mempoolBlocksFull: MempoolBlock[] = [];
@@ -57,10 +58,8 @@ export class MempoolBlocksComponent implements OnInit, OnChanges, OnDestroy {
   network = '';
   now = new Date().getTime();
   timeOffset = 0;
-  showMiningInfo = false;
   timeLtrSubscription: Subscription;
   timeLtr: boolean;
-  showMiningInfoSubscription: Subscription;
   animateEntry: boolean = false;
 
   blockOffset: number = 155;
@@ -98,10 +97,7 @@ export class MempoolBlocksComponent implements OnInit, OnChanges, OnDestroy {
     this.widthChange.emit(this.mempoolWidth);
 
     if (['', 'testnet', 'signet'].includes(this.stateService.network)) {
-      this.showMiningInfoSubscription = this.stateService.showMiningInfo$.subscribe((showMiningInfo) => {
-        this.showMiningInfo = showMiningInfo;
-        this.cd.markForCheck();
-      });
+      this.showMiningInfo$ = this.stateService.showMiningInfo$;
     }
 
     this.timeLtrSubscription = this.stateService.timeLtr.subscribe((ltr) => {
@@ -267,7 +263,6 @@ export class MempoolBlocksComponent implements OnInit, OnChanges, OnDestroy {
     this.chainTipSubscription.unsubscribe();
     this.keySubscription.unsubscribe();
     this.isTabHiddenSubscription.unsubscribe();
-    this.showMiningInfoSubscription.unsubscribe();
     clearTimeout(this.resetTransitionTimeout);
   }
 
```
