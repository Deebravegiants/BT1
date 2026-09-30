# [?] fix: resolve database deadlock: (#4989)

## Summary
Severity: Unknown
Chain: XRP
Component: XRPLF/rippled
Published: 2024-04-18
Source: https://github.com/XRPLF/rippled/commit/cd737ad7d31be228b00d81c7ad121b6fbcbb00ce
Type: security-commit

## Details
fix: resolve database deadlock: (#4989)

The `rotateWithLock` function holds a lock while it calls a callback
function that's passed in by the caller. This is a problematic design
that needs to be used very carefully. In this case, at least one caller
passed in a callback that eventually relocks the mutex on the same
thread, causing UB (a deadlock was observed). The caller was from
SHAMapStoreImpl, and it called `clearCaches`. This `clearCaches` can
potentially call `fetchNodeObject`, which tried to relock the mutex.

This patch resolves the issue by changing the mutex type to a
`recursive_mutex`. Ideally, the code should be rewritten so it doesn't
hold the mutex during the callback and the mutex should be changed back
to a regular mutex.

Co-authored-by: Ed Hennis <ed@ripple.com>

## Patch
### src/ripple/nodestore/impl/DatabaseRotatingImp.h
```diff
@@ -22,6 +22,8 @@
 
 #include <ripple/nodestore/DatabaseRotating.h>
 
+#include <mutex>
+
 namespace ripple {
 namespace NodeStore {
 
@@ -82,7 +84,13 @@ class DatabaseRotatingImp : public DatabaseRotating
 private:
     std::shared_ptr<Backend> writableBackend_;
     std::shared_ptr<Backend> archiveBackend_;
-    mutable std::mutex mutex_;
+    // This needs to be a recursive mutex because callbacks in `rotateWithLock`
+    // can call function that also lock the mutex. A current example of this is
+    // a callback from SHAMapStoreImp, which calls `clearCaches`. This
+    // `clearCaches` call eventually calls `fetchNodeObject` which tries to
+    // relock the mutex. It would be desirable to rewrite the code so the lock
+    // was not held during a callback.
+    mutable std::recursive_mutex mutex_;
 
     std::shared_ptr<NodeObject>
     fetchNodeObject(
```
