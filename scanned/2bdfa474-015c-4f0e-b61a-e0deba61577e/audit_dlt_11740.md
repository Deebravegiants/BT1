# [?] Fix price fetching causing race condition

## Summary
Severity: Unknown
Chain: Bitcoin
Component: mempool/mempool
Published: 2024-06-12
Source: https://github.com/mempool/mempool/commit/824bf5fc636d495fa9107ed7122fdcd8f3577af2
Type: security-commit

## Details
Fix price fetching causing race condition

## Patch
### frontend/src/app/components/address-graph/address-graph.component.ts
```diff
@@ -1,7 +1,7 @@
 import { ChangeDetectionStrategy, ChangeDetectorRef, Component, Inject, Input, LOCALE_ID, OnChanges, OnDestroy, SimpleChanges } from '@angular/core';
 import { echarts, EChartsOption } from '../../graphs/echarts';
 import { BehaviorSubject, Observable, Subscription, combineLatest, of } from 'rxjs';
-import { catchError, tap } from 'rxjs/operators';
+import { catchError, map, switchMap, tap } from 'rxjs/operators';
 import { AddressTxSummary, ChainStats } from '../../interfaces/electrs.interface';
 import { ElectrsApiService } from '../../services/electrs-api.service';
 import { AmountShortenerPipe } from '../../shared/pipes/amount-shortener.pipe';
@@ -47,6 +47,7 @@ export class AddressGraphComponent implements OnChanges, OnDestroy {
   @Input() widget: boolean = false;
 
   data: any[] = [];
+  fiatData: any[] = [];
   hoverData: any[] = [];
   showFiat = false;
   conversions: any;
@@ -97,7 +98,32 @@ export class AddressGraphComponent implements OnChanges, OnDestroy {
           }),
         )),
         this.stateService.conversions$
-      ]).subscribe(([redraw, addressSummary, conversions]) => {
+      ]).pipe(
+        switchMap(([redraw, addressSummary, conversions]) => {
+          if (addressSummary) {
+            return this.priceService.getPriceByBulk$(addressSummary.map(d => d.time), 'USD').pipe(
+              tap((prices) => {
+                if (prices.length !== addressSummary.length) {
+                  addressSummary = addressSummary.map(item => ({ ...item, price: 0 }));
+                } else {
+                  addressSummary = addressSummary.map((item, index) => {
+                    let price = 0;
+                    if (prices[index].price) {
+                      price = prices[index].price['USD'];
+                    } else if (this.conversions && this.conversions['USD']) {
+                      price = this.conversions['USD'];
+                    }
+                    return { ...item, price: price }
+                  });
+                }
+              }),
+              map(() => [redraw, addressSummary, conversions])
+            )
+          } else {
+            return of([redraw, addressSummary, conversions]);
+          }
+        })
+      ).subscribe(([redraw, addressSummary, conversions]) => {
         if (addressSummary) {
           this.error = null;
           this.conversions = conversions;
@@ -117,41 +143,35 @@ export class AddressGraphComponent implements OnChanges, OnDestroy {
     if (!summary || !this.stats) {
       return;
     }
-
-    this.priceService.getPriceByBulk$(summary.map(d => d.time), 'USD').pipe(
-      tap((prices) => {
-        if (prices.length !== summary.length) {
-          summary = summary.map(item => ({ ...item, price: 0 }));
-        } else {
-          summary = summary.map((item, index) => {
-            let price = 0;
-            if (prices[index].price) {
-              price = prices[index].price['USD'];
-            } else if (this.conversions['USD']) {
-              price = this.conversions['USD'];
-            }
-            return { ...item, price: price }
-          });
-        }
-      })
-    ).subscribe();
     
     let total = (this.stats.funded_txo_sum - this.stats.spent_txo_sum);
-    this.data = summary.map(d => {
-      const balance = total;
-      const fiatValue = balance * d.price / 100_000_000;
-      total -= d.value;
-      d.fiatValue = d.value * d.price / 100_000_000;
-      return [d.time * 1000, balance, d, fiatValue];
+    const processData = summary.map(d => {
+        const balance = total;
+        const fiatBalance = total * d.price / 100_000_000;
+        total -= d.value;
+        d.fiatValue = d.value * d.price / 100_000_000;
+        return {
+            time: d.time * 1000,
+            balance,
+            fiatBalance,
+            d
+        };
     }).reverse();
+    
+    this.data = processData.map(({ time, balance, d }) => [time, balance, d]);
+    this.fiatData = processData.map(({ time, fiatBalance, d }) => [time, fiatBalance, d]);
 
     if (this.period !== 'all') {
       const now = Date.now();
       const start = now - (periodSeconds[this.period] * 1000);
       this.data = this.data.filter(d => d[0] >= start);
+      this.fiatData = this.fiatData.filter(d => d[0] >= start);
       this.data.push(
         {value: [now, this.stats.funded_txo_sum - this.stats.spent_txo_sum], symbol: 'none', tooltip: { show: false }}
       );
+      this.fiatData.push(
+        {value: [now, this.fiatData[this.fiatData.length - 1][1]], symbol: 'none', tooltip: { show: false }}
+      );
     }
 
     const maxValue = this.data.reduce((acc, d) => Math.max(acc, Math.abs(d[1] ?? d.value[1])), 0);
@@ -314,7 +334,7 @@ export class AddressGraphComponent implements OnChanges, OnDestroy {
           showSymbol: false,
           symbol: 'circle',
           symbolSize: 8,
-          data: this.data.map(d => [d[0], d[1], d[2]]),
+          data: this.data,
           areaStyle: {
             opacity: 0.5,
           },
@@ -329,7 +349,7 @@ export class AddressGraphComponent implements OnChanges, OnDestroy {
           showSymbol: false,
           symbol: 'circle',
           symbolSize: 8,
-          data: this.data.map(d => [d[0], d[3], d[2]]),
+          data: this.fiatData,
           areaStyle: {
             opacity: 0.5,
           },
```
