# [?] Merge #568: Fix integer overflow in ecmult_multi_var when n is large

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoin-core/secp256k1
Published: 2019-02-25
Source: https://github.com/bitcoin-core/secp256k1/commit/aa15154a4882a40227a238edef830b85a4942d4f
Type: security-commit

## Details
Merge #568: Fix integer overflow in ecmult_multi_var when n is large

2277af5 Fix integer overflow in ecmult_multi_var when n is large (Jonas Nick)

Pull request description:

  Without this PR ecmult_multi could return wrong results. If the number of points `n` is large enough then some or all multiplications could be skipped or the function could end up in an infinite loop. This PR adds two checks to prevent `n` from wrapping around.

Tree-SHA512: 342944369b24776fa3ec0694eee159259ff67e94d2d8176c1d3159875f387d943d5bfdff7cde59f058e13f07fd09bde1cbc609426e63c8a5b8040e382dd865d8

## Patch
### src/ecmult_impl.h
```diff
@@ -1111,12 +1111,31 @@ static int secp256k1_ecmult_multi_simple_var(const secp256k1_ecmult_context *ctx
     return 1;
 }
 
+/* Compute the number of batches and the batch size given the maximum batch size and the
+ * total number of points */
+static int secp256k1_ecmult_multi_batch_size_helper(size_t *n_batches, size_t *n_batch_points, size_t max_n_batch_points, size_t n) {
+    if (max_n_batch_points == 0) {
+        return 0;
+    }
+    if (max_n_batch_points > ECMULT_MAX_POINTS_PER_BATCH) {
+        max_n_batch_points = ECMULT_MAX_POINTS_PER_BATCH;
+    }
+    if (n == 0) {
+        *n_batches = 0;
+        *n_batch_points = 0;
+        return 1;
+    }
+    /* Compute ceil(n/max_n_batch_points) and ceil(n/n_batches) */
+    *n_batches = 1 + (n - 1) / max_n_batch_points;
+    *n_batch_points = 1 + (n - 1) / *n_batches;
+    return 1;
+}
+
 typedef int (*secp256k1_ecmult_multi_func)(const secp256k1_ecmult_context*, secp256k1_scratch*, secp256k1_gej*, const secp256k1_scalar*, secp256k1_ecmult_multi_callback cb, void*, size_t);
 static int secp256k1_ecmult_multi_var(const secp256k1_ecmult_context *ctx, secp256k1_scratch *scratch, secp256k1_gej *r, const secp256k1_scalar *inp_g_sc, secp256k1_ecmult_multi_callback cb, void *cbdata, size_t n) {
     size_t i;
 
     int (*f)(const secp256k1_ecmult_context*, secp256k1_scratch*, secp256k1_gej*, const secp256k1_scalar*, secp256k1_ecmult_multi_callback cb, void*, size_t, size_t);
-    size_t max_points;
     size_t n_batches;
     size_t n_batch_points;
 
@@ -1133,24 +1152,17 @@ static int secp256k1_ecmult_multi_var(const secp256k1_ecmult_context *ctx, secp2
         return secp256k1_ecmult_multi_simple_var(ctx, r, inp_g_sc, cb, cbdata, n);
     }
 
-    max_points = secp256k1_pippenger_max_points(scratch);
-    if (max_points == 0) {
+    /* Compute the batch sizes for pippenger given a scratch space. If it's greater than a threshold
+     * use pippenger. Otherwise use strauss */
+    if (!secp256k1_ecmult_multi_batch_size_helper(&n_batches, &n_batch_points, secp256k1_pippenger_max_points(scratch), n)) {
         return 0;
-    } else if (max_points > ECMULT_MAX_POINTS_PER_BATCH) {
-        max_points = ECMULT_MAX_POINTS_PER_BATCH;
     }
-    n_batches = (n+max_points-1)/max_points;
-    n_batch_points = (n+n_batches-1)/n_batches;
-
     if (n_batch_points >= ECMULT_PIPPENGER_THRESHOLD) {
         f = secp256k1_ecmult_pippenger_batch;
     } else {
-        max_points = secp256k1_strauss_max_points(scratch);
-        if (max_points == 0) {
+        if (!secp256k1_ecmult_multi_batch_size_helper(&n_batches, &n_batch_points, secp256k1_strauss_max_points(scratch), n)) {
             return 0;
         }
-        n_batches = (n+max_points-1)/max_points;
-        n_batch_points = (n+n_batches-1)/n_batches;
         f = secp256k1_ecmult_strauss_batch;
     }
     for(i = 0; i < n_batches; i++) {
```

### src/tests.c
```diff
@@ -2854,6 +2854,50 @@ void test_ecmult_multi_pippenger_max_points(void) {
     CHECK(bucket_window == PIPPENGER_MAX_BUCKET_WINDOW);
 }
 
+void test_ecmult_multi_batch_size_helper(void) {
+    size_t n_batches, n_batch_points, max_n_batch_points, n;
+
+    max_n_batch_points = 0;
+    n = 1;
+    CHECK(secp256k1_ecmult_multi_batch_size_helper(&n_batches, &n_batch_points, max_n_batch_points, n) == 0);
+
+    max_n_batch_points = 1;
+    n = 0;
+    CHECK(secp256k1_ecmult_multi_batch_size_helper(&n_batches, &n_batch_points, max_n_batch_points, n) == 1);
+    CHECK(n_batches == 0);
+    CHECK(n_batch_points == 0);
+
+    max_n_batch_points = 2;
+    n = 5;
+    CHECK(secp256k1_ecmult_multi_batch_size_helper(&n_batches, &n_batch_points, max_n_batch_points, n) == 1);
+    CHECK(n_batches == 3);
+    CHECK(n_batch_points == 2);
+
+    max_n_batch_points = ECMULT_MAX_POINTS_PER_BATCH;
+    n = ECMULT_MAX_POINTS_PER_BATCH;
+    CHECK(secp256k1_ecmult_multi_batch_size_helper(&n_batches, &n_batch_points, max_n_batch_points, n) == 1);
+    CHECK(n_batches == 1);
+    CHECK(n_batch_points == ECMULT_MAX_POINTS_PER_BATCH);
+
+    max_n_batch_points = ECMULT_MAX_POINTS_PER_BATCH + 1;
+    n = ECMULT_MAX_POINTS_PER_BATCH + 1;
+    CHECK(secp256k1_ecmult_multi_batch_size_helper(&n_batches, &n_batch_points, max_n_batch_points, n) == 1);
+    CHECK(n_batches == 2);
+    CHECK(n_batch_points == ECMULT_MAX_POINTS_PER_BATCH/2 + 1);
+
+    max_n_batch_points = 1;
+    n = SIZE_MAX;
+    CHECK(secp256k1_ecmult_multi_batch_size_helper(&n_batches, &n_batch_points, max_n_batch_points, n) == 1);
+    CHECK(n_batches == SIZE_MAX);
+    CHECK(n_batch_points == 1);
+
+    max_n_batch_points = 2;
+    n = SIZE_MAX;
+    CHECK(secp256k1_ecmult_multi_batch_size_helper(&n_batches, &n_batch_points, max_n_batch_points, n) == 1);
+    CHECK(n_batches == SIZE_MAX/2 + 1);
+    CHECK(n_batch_points == 2);
+}
+
 /**
  * Run secp256k1_ecmult_multi_var with num points and a scratch space restricted to
  * 1 <= i <= num points.
@@ -2936,6 +2980,7 @@ void run_ecmult_multi_tests(void) {
     test_ecmult_multi(scratch, secp256k1_ecmult_multi_var);
     secp256k1_scratch_destroy(scratch);
 
+    test_ecmult_multi_batch_size_helper();
     test_ecmult_multi_batching();
 }
 
```
