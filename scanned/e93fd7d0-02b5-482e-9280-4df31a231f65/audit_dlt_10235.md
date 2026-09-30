# [?] prb3-monitor: fix crash

## Summary
Severity: Unknown
Chain: Phala
Component: Phala-Network/phala-blockchain
Published: 2023-05-09
Source: https://github.com/Phala-Network/phala-blockchain/commit/aedb961c784e9d9c1cb43b41eea27558e5e30d81
Type: security-commit

## Details
prb3-monitor: fix crash

## Patch
### frontend/apps/prb3-monitor/src/pages/status/tx.js
```diff
@@ -14,7 +14,7 @@ import Column from 'baseui/data-table/column';
 const columns = [
   NumericalColumn({
     title: 'ID',
-    mapDataToValue: (data) => data.id,
+    mapDataToValue: (data) => data.id || '',
   }),
   CategoricalColumn({
     title: 'PID',
```

### frontend/apps/prb3-monitor/src/pages/status/worker.js
```diff
@@ -36,7 +36,7 @@ const columns = [
   CategoricalColumn({
     title: 'Session S.',
     mapDataToValue: (data) => {
-      return data.session_info?.state;
+      return data.session_info?.state || '';
     },
   }),
   Column({
@@ -55,7 +55,7 @@ const columns = [
     mapDataToValue: (data) => {
       const s = data?.state;
       const e = s?.HasError;
-      return (e ? `(From error state) ${e}` : '') + '\n' + data.last_message;
+      return (e ? `(From error state) ${e}` : '') + '\n' + (data.last_message || '');
     },
     textQueryFilter: function (textQuery, data) {
       return data.toLowerCase().includes(textQuery.toLowerCase());
@@ -85,15 +85,15 @@ const columns = [
   }),
   StringColumn({
     title: 'Public Key',
-    mapDataToValue: (data) => data.phactory_info?.public_key,
+    mapDataToValue: (data) => data.phactory_info?.public_key || '',
   }),
   CategoricalColumn({
     title: 'pRuntime Version',
-    mapDataToValue: (data) => data.phactory_info?.version,
+    mapDataToValue: (data) => data.phactory_info?.version || '',
   }),
   CategoricalColumn({
     title: 'pRuntime Git Rev.',
-    mapDataToValue: (data) => data.phactory_info?.git_revision,
+    mapDataToValue: (data) => data.phactory_info?.git_revision || '',
   }),
   NumericalColumn({
     title: 'rust_peak_used',
@@ -109,7 +109,7 @@ const columns = [
   }),
   StringColumn({
     title: 'UUID',
-    mapDataToValue: (data) => data.worker.id,
+    mapDataToValue: (data) => data.worker.id || '',
   }),
 ];
 
```
