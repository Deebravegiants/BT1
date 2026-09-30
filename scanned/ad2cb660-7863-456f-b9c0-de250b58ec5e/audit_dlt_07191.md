# [?] Fixed deadlock and crash when syncing with full dataset on Windows

## Summary
Severity: Unknown
Chain: Monero
Component: monero-project/monero
Published: 2023-03-29
Source: https://github.com/monero-project/monero/commit/d59498101c5e48fe71ddfc189086b895f3f8ce76
Type: security-commit

## Details
Fixed deadlock and crash when syncing with full dataset on Windows

It's not allowed to use WaitForSingleObject with _beginthread, because the thread closes its own handle before exiting.

So the wait function will either wait on an invalid handle, or on a different handle used by something else.

Or, if it starts waiting before the thread exits, the behavior is undefined according to MS: "If this handle is closed while the wait is still pending, the function's behavior is undefined."

In my test sync I observed threads getting stuck infinitely on WaitForSingleObject, and then rx_set_main_seedhash spamming new threads when RandomX seed changes again. Eventually the system ran out of resources, and monerod aborted with "Couldn't start RandomX seed thread" message.

This PR fixes it by using `_beginthreadex` instead and explicitly closing the handle when it's safe.

## Patch
### src/crypto/c_threads.h
```diff
@@ -42,10 +42,11 @@
 #define CTHR_RWLOCK_TRYLOCK_READ(x)	TryAcquireSRWLockShared(&x)
 
 #define CTHR_THREAD_TYPE	HANDLE
-#define CTHR_THREAD_RTYPE	void
-#define CTHR_THREAD_RETURN	return
-#define CTHR_THREAD_CREATE(thr, func, arg)	((thr = (HANDLE)_beginthread(func, 0, arg)) != -1L)
-#define CTHR_THREAD_JOIN(thr)			WaitForSingleObject((HANDLE)thr, INFINITE)
+#define CTHR_THREAD_RTYPE	unsigned __stdcall
+#define CTHR_THREAD_RETURN	_endthreadex(0); return 0;
+#define CTHR_THREAD_CREATE(thr, func, arg)	((thr = (HANDLE)_beginthreadex(0, 0, func, arg, 0, 0)) != 0L)
+#define CTHR_THREAD_JOIN(thr)			do { WaitForSingleObject(thr, INFINITE); CloseHandle(thr); } while(0)
+#define CTHR_THREAD_CLOSE(thr)			CloseHandle((HANDLE)thr);
 
 #else
 
@@ -64,5 +65,6 @@
 #define CTHR_THREAD_RETURN	return NULL
 #define CTHR_THREAD_CREATE(thr, func, arg)	(pthread_create(&thr, NULL, func, arg) == 0)
 #define CTHR_THREAD_JOIN(thr)			pthread_join(thr, NULL)
+#define CTHR_THREAD_CLOSE(thr)
 
 #endif
```

### src/crypto/rx-slow-hash.c
```diff
@@ -332,7 +332,7 @@ static void rx_init_dataset(size_t max_threads) {
       local_abort("Couldn't start RandomX seed thread");
     }
   }
-  rx_seedthread(&si[n1]);
+  randomx_init_dataset(main_dataset, si[n1].si_cache, si[n1].si_start, si[n1].si_count);
   for (size_t i = 0; i < n1; ++i) CTHR_THREAD_JOIN(st[i]);
   CTHR_RWLOCK_UNLOCK_READ(main_cache_lock);
 
@@ -402,6 +402,7 @@ void rx_set_main_seedhash(const char *seedhash, size_t max_dataset_init_threads)
   if (!CTHR_THREAD_CREATE(t, rx_set_main_seedhash_thread, info)) {
     local_abort("Couldn't start RandomX seed thread");
   }
+  CTHR_THREAD_CLOSE(t);
 }
 
 void rx_slow_hash(const char *seedhash, const void *data, size_t length, char *result_hash) {
```
