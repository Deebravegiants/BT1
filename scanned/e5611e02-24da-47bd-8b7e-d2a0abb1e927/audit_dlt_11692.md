# [?] Merge bitcoin-core/secp256k1#1910: scratch: reject sizes that overflow when added to header

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoin-core/secp256k1
Published: 2026-08-16
Source: https://github.com/bitcoin-core/secp256k1/commit/439278a649d3099d62dde966a76dc04aaca7ccb3
Type: security-commit

## Details
Merge bitcoin-core/secp256k1#1910: scratch: reject sizes that overflow when added to header

3d4340d17325a6732108423f9d3e54de99539a60 scratch: reject sizes that overflow when added to header (Sebastian Falbesoner)

Pull request description:

  We only use scratch space internally, so this is not an issue for the user (scratch API functions have been removed since 0.6.0, see #1620), but fixing this might still make sense to prepare for the unlikely case that we expose the scratch API again in the future. An alternative could be to simply delete the scratch space functionality already, as e.g. done in PR #1789.

  Reported by [Project Loupe](https://github.com/project-loupe)

ACKs for top commit:
  apoelstra:
    utACK 3d4340d17325a6732108423f9d3e54de99539a60
  real-or-random:
    utACK 3d4340d17325a6732108423f9d3e54de99539a60

Tree-SHA512: 8e380919a48445d8df46a568e4fcbcbe31b5b5668586942d1eaa1b90b4e0669548d5ca831c8dde484b869c7e95faacb608491738a59c5e1ee15d4084acc7ead6

## Patch
### src/scratch_impl.h
```diff
@@ -12,8 +12,14 @@
 
 static secp256k1_scratch* secp256k1_scratch_create(const secp256k1_callback* error_callback, size_t size) {
     const size_t base_alloc = ROUND_TO_ALIGN(sizeof(secp256k1_scratch));
-    void *alloc = checked_malloc(error_callback, base_alloc + size);
-    secp256k1_scratch* ret = (secp256k1_scratch *)alloc;
+    void *alloc;
+    secp256k1_scratch* ret;
+    /* Reject sizes that would wrap when added to the aligned header. */
+    if (size > SIZE_MAX - base_alloc) {
+        return NULL;
+    }
+    alloc = checked_malloc(error_callback, base_alloc + size);
+    ret = (secp256k1_scratch *)alloc;
     if (ret != NULL) {
         memset(ret, 0, sizeof(*ret));
         memcpy(ret->magic, "scratch", 8);
```

### src/tests.c
```diff
@@ -420,6 +420,12 @@ static void run_scratch_tests(void) {
     CHECK(secp256k1_scratch_alloc(&CTX->error_callback, scratch, SIZE_MAX) == NULL);
     secp256k1_scratch_space_destroy(CTX, scratch);
 
+    /* Creating a scratch space whose size would wrap around when the aligned
+     * header size is added to it fails, both for SIZE_MAX and for the smallest
+     * size that still wraps. */
+    CHECK(secp256k1_scratch_space_create(CTX, SIZE_MAX) == NULL);
+    CHECK(secp256k1_scratch_space_create(CTX, SIZE_MAX - ROUND_TO_ALIGN(sizeof(secp256k1_scratch)) + 1) == NULL);
+
     /* cleanup */
     secp256k1_scratch_space_destroy(CTX, NULL); /* no-op */
 }
```
