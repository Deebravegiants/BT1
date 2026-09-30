# [?] Merge pull request #5871 from mempool/natsoni/fix-liquid-overflow

## Summary
Severity: Unknown
Chain: Bitcoin
Component: mempool/mempool
Published: 2025-04-13
Source: https://github.com/mempool/mempool/commit/215a65efccf0a980f19b04a8b5d41bf1297d2673
Type: security-commit

## Details
Merge pull request #5871 from mempool/natsoni/fix-liquid-overflow

Fix liquid scroll overflow

## Patch
### frontend/src/app/components/timezone-selector/timezone-selector.component.html
```diff
@@ -1,4 +1,4 @@
-<div [formGroup]="timezoneForm" class="text-small text-center">
+<div [formGroup]="timezoneForm" class="text-small text-center" style="overflow-x: hidden;">
     <select formControlName="mode" class="custom-select custom-select-sm form-control-secondary form-control mx-auto" style="width: 110px;" (change)="changeMode()">
         <option value="local">UTC{{ localTimezoneOffset !== '+0' ? localTimezoneOffset : '' }} {{ localTimezoneName ? '- ' + localTimezoneName : '' }}</option>
         <option value="+0" *ngIf="localTimezoneOffset !== '+0'">UTC - Greenwich Mean Time (GMT)</option>
```
