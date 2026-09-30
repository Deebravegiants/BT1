# [?] Fix out-of-bounds write in case of failing mmap(...) in PosixLockedPageAllocator::AllocateLocked

## Summary
Severity: Unknown
Chain: Zcash
Component: zcash/zcash
Published: 2019-01-06
Source: https://github.com/zcash/zcash/commit/3d635dd09fe3dcbeba423d68d2be96414daf05aa
Type: security-commit

## Details
Fix out-of-bounds write in case of failing mmap(...) in PosixLockedPageAllocator::AllocateLocked

## Patch
### src/support/allocators/secure.h
```diff
@@ -40,7 +40,11 @@ struct secure_allocator : public std::allocator<T> {
 
     T* allocate(std::size_t n, const void* hint = 0)
     {
-        return static_cast<T*>(LockedPoolManager::Instance().alloc(sizeof(T) * n));
+        T* allocation = static_cast<T*>(LockedPoolManager::Instance().alloc(sizeof(T) * n));
+        if (!allocation) {
+            throw std::bad_alloc();
+        }
+        return allocation;
     }
 
     void deallocate(T* p, std::size_t n)
```

### src/support/lockedpool.cpp
```diff
@@ -248,6 +248,9 @@ void *PosixLockedPageAllocator::AllocateLocked(size_t len, bool *lockingSuccess)
     void *addr;
     len = align_up(len, page_size);
     addr = mmap(nullptr, len, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0);
+    if (addr == MAP_FAILED) {
+        return nullptr;
+    }
     if (addr) {
         *lockingSuccess = mlock(addr, len) == 0;
     }
```

### src/support/lockedpool.h
```diff
@@ -22,7 +22,7 @@ class LockedPageAllocator
     virtual ~LockedPageAllocator() {}
     /** Allocate and lock memory pages.
      * If len is not a multiple of the system page size, it is rounded up.
-     * Returns 0 in case of allocation failure.
+     * Returns nullptr in case of allocation failure.
      *
      * If locking the memory pages could not be accomplished it will still
      * return the memory, however the lockingSuccess flag will be false.
```
