# [?] [accelerator] fix overflow in tx page integrated accel

## Summary
Severity: Unknown
Chain: Bitcoin
Component: mempool/mempool
Published: 2023-08-26
Source: https://github.com/mempool/mempool/commit/1fe08d1234d6cfcdbbe22d1aabfc9048e58a3ce9
Type: security-commit

## Details
[accelerator] fix overflow in tx page integrated accel

## Patch
### frontend/src/app/components/accelerate-preview/accelerate-preview.component.html
```diff
@@ -24,7 +24,7 @@
   <div [class]="{estimateDisabled: error}">
     <div class="row mb-3">
       <div class="col">
-        <table class="table table-borderless table-border table-dark">
+        <table class="table table-borderless table-border table-dark table-accelerator">
           <tbody>
             <!-- NEXT BLOCK TX FEE -->
             <tr>
@@ -110,7 +110,7 @@ <h6>How much more are you willing to pay at most to get into the next block?</h6
     <h6>Acceleration summary</h6>
     <div class="row mb-3">
       <div class="col">
-        <table class="table table-borderless table-border table-dark">
+        <table class="table table-borderless table-border table-dark table-accelerator">
           <tbody>
             <!-- USER MAX BID -->
             <tr>
```

### frontend/src/app/components/accelerate-preview/accelerate-preview.component.scss
```diff
@@ -18,3 +18,10 @@
   opacity: 0.5;
   pointer-events: none;
 }
+
+.table-accelerator {
+  table-layout: fixed;
+  & tr {
+    text-wrap: wrap;
+  }
+}
\ No newline at end of file
```
