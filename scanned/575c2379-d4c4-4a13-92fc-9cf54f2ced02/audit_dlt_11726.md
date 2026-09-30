# [?] Fix USD y axis overflow in address graph

## Summary
Severity: Unknown
Chain: Bitcoin
Component: mempool/mempool
Published: 2024-11-19
Source: https://github.com/mempool/mempool/commit/7516db0c71576b2f16c9d70652482c01ac1719c0
Type: security-commit

## Details
Fix USD y axis overflow in address graph

## Patch
### frontend/src/app/components/address-graph/address-graph.component.ts
```diff
@@ -10,7 +10,6 @@ import { RelativeUrlPipe } from '@app/shared/pipes/relative-url/relative-url.pip
 import { StateService } from '@app/services/state.service';
 import { PriceService } from '@app/services/price.service';
 import { FiatCurrencyPipe } from '@app/shared/pipes/fiat-currency.pipe';
-import { FiatShortenerPipe } from '@app/shared/pipes/fiat-shortener.pipe';
 
 const periodSeconds = {
   '1d': (60 * 60 * 24),
@@ -77,7 +76,6 @@ export class AddressGraphComponent implements OnChanges, OnDestroy {
     private relativeUrlPipe: RelativeUrlPipe,
     private priceService: PriceService,
     private fiatCurrencyPipe: FiatCurrencyPipe,
-    private fiatShortenerPipe: FiatShortenerPipe,
     private zone: NgZone,
   ) {}
 
@@ -336,7 +334,7 @@ export class AddressGraphComponent implements OnChanges, OnDestroy {
           axisLabel: {
             color: 'rgb(110, 112, 121)',
             formatter: function(val) {
-              return this.fiatShortenerPipe.transform(val, null, 'USD');
+              return `$${this.amountShortenerPipe.transform(val, 0)}`;
             }.bind(this)
           },
           splitLine: {
```
