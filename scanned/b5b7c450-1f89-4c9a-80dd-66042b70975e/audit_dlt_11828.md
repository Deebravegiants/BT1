# [?] Fix potential race condition in the cache when thread can't get the lock

## Summary
Severity: Unknown
Chain: Tooling
Component: ApeWorX/web3.py
Published: 2023-06-03
Source: https://github.com/ApeWorX/web3.py/commit/1cc6896a50f35a3f9608c0ebfc03afb5eef7aaca
Type: security-commit

## Details
Fix potential race condition in the cache when thread can't get the lock

## Patch
### web3/middleware/cache.py
```diff
@@ -103,11 +103,11 @@ def middleware(method: RPCEndpoint, params: Any) -> RPCResponse:
 
                 response = make_request(method, params)
                 if should_cache_fn(method, params, response):
-                    lock.acquire(blocking=False)
-                    try:
-                        cache.cache(cache_key, response)
-                    finally:
-                        lock.release()
+                    if lock.acquire(blocking=False):
+                        try:
+                            cache.cache(cache_key, response)
+                        finally:
+                            lock.release()
                 return response
             else:
                 return make_request(method, params)
```
