# [?] Fix use-after-free possible during shutdown-while-indexing edge case.

## Summary
Severity: Unknown
Chain: Stellar
Component: stellar/stellar-core
Published: 2025-08-13
Source: https://github.com/stellar/stellar-core/commit/4591d19aeb1268f98f0664c0a5ad91b05309f527
Type: security-commit

## Details
Fix use-after-free possible during shutdown-while-indexing edge case.

## Patch
### src/historywork/VerifyBucketWork.cpp
```diff
@@ -77,7 +77,7 @@ VerifyBucketWork<BucketT>::spawnVerifier()
     std::weak_ptr<VerifyBucketWork> weak(
         std::static_pointer_cast<VerifyBucketWork>(shared_from_this()));
     app.postOnBackgroundThread(
-        [&app, filename, weak, hash, &index = mIndex]() {
+        [&app, filename, weak, hash]() {
             SHA256 hasher;
             asio::error_code ec;
 
@@ -88,6 +88,7 @@ VerifyBucketWork<BucketT>::spawnVerifier()
                 return;
             }
 
+            std::unique_ptr<typename BucketT::IndexT const> index;
             try
             {
                 ZoneNamedN(verifyZone, "bucket verify", true);
@@ -97,6 +98,10 @@ VerifyBucketWork<BucketT>::spawnVerifier()
                 index =
                     createIndex<BucketT>(app.getBucketManager(), filename, hash,
                                          app.getWorkerIOContext(), &hasher);
+                if (self->isAborting())
+                {
+                    return;
+                }
                 releaseAssertOrThrow(index);
 
                 uint256 vHash = hasher.finish();
@@ -121,14 +126,22 @@ VerifyBucketWork<BucketT>::spawnVerifier()
                 ec = std::make_error_code(std::errc::io_error);
             }
 
+            // This is a bit silly but std::function has to be copyable.
+            auto shared_index =
+                std::make_shared<decltype(index)>(std::move(index));
+
             // Not ideal, but needed to prevent race conditions with
             // main thread, since BasicWork's state is not thread-safe. This is
             // a temporary workaround, as a cleaner solution is needed.
             app.postOnMainThread(
-                [weak, ec]() {
+                [weak, ec, shared_index]() {
                     auto self = weak.lock();
                     if (self)
                     {
+                        if (!self->isAborting() && *shared_index)
+                        {
+                            self->mIndex = std::move(*shared_index);
+                        }
                         self->mEc = ec;
                         self->mDone = true;
                         self->wakeUp();
```
