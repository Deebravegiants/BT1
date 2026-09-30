# [?] Fix custom dashboard address widgets race condition

## Summary
Severity: Unknown
Chain: Bitcoin
Component: mempool/mempool
Published: 2026-06-10
Source: https://github.com/mempool/mempool/commit/d58061ebc0fa641ab1b24a03e18940dc17c1816c
Type: security-commit

## Details
Fix custom dashboard address widgets race condition

## Patch
### frontend/src/app/components/custom-dashboard/custom-dashboard.component.ts
```diff
@@ -1,6 +1,6 @@
 import { AfterViewInit, ChangeDetectionStrategy, ChangeDetectorRef, Component, HostListener, Inject, OnDestroy, OnInit, PLATFORM_ID } from '@angular/core';
 import { combineLatest, merge, Observable, of, Subject, Subscription } from 'rxjs';
-import { catchError, filter, map, scan, share, shareReplay, startWith, switchMap, tap } from 'rxjs/operators';
+import { catchError, filter, map, scan, shareReplay, startWith, switchMap, tap } from 'rxjs/operators';
 import { BlockExtended, OptimizedMempoolStats, TransactionStripped } from '@interfaces/node-api.interface';
 import { MempoolInfo, ReplacementInfo } from '@interfaces/websocket.interface';
 import { ApiService } from '@app/services/api.service';
@@ -360,7 +360,7 @@ export class CustomDashboardComponent implements OnInit, OnDestroy, AfterViewIni
             return summary;
           }, initial)
         )),
-        share(),
+        shareReplay({ bufferSize: 1, refCount: true }),
       );
     }
   }
@@ -412,7 +412,7 @@ export class CustomDashboardComponent implements OnInit, OnDestroy, AfterViewIni
             return this.deduplicateWalletTransactions([...summaries, ...newSummaries]);
           }, this.deduplicateWalletTransactions(Object.values(wallet).flatMap(address => address.transactions)))
         )),
-        share(),
+        shareReplay({ bufferSize: 1, refCount: true }),
       );
     }
   }
```
