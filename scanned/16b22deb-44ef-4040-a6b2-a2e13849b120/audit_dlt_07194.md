# [?] miner: fix possible exit crash due to race in stop

## Summary
Severity: Unknown
Chain: Monero
Component: monero-project/monero
Published: 2019-03-14
Source: https://github.com/monero-project/monero/commit/39f000b3948e64a38b14b1d358ced1b2d1f44bf3
Type: security-commit

## Details
miner: fix possible exit crash due to race in stop

If a thread asks to stop the miner, m_stop will be set, and
that thread will wait to join. If the main thread is exiting
at that time, it will ask the miner to stop, but the miner
will claim it's not mining and early out since m_stop is
set. This will cause the database and other things to get
shutdown. If the miner happens to find a block at that time,
it will try to call core, and crash.

Instead, lock and check whether any threads are currently
in m_threads, since they'll only be cleared once the threads
are joined. Moreover, since we lock, the second thread will
have to wait for the first one to have finished. Calling
join twice on a thread seems fine as per pthread_join(3).

## Patch
### src/cryptonote_basic/miner.cpp
```diff
@@ -432,14 +432,15 @@ namespace cryptonote
   {
     MTRACE("Miner has received stop signal");
 
-    if (!is_mining())
+    CRITICAL_REGION_LOCAL(m_threads_lock);
+    bool mining = !m_threads.empty();
+    if (!mining)
     {
       MTRACE("Not mining - nothing to stop" );
       return true;
     }
 
     send_stop_signal();
-    CRITICAL_REGION_LOCAL(m_threads_lock);
 
     // In case background mining was active and the miner threads are waiting
     // on the background miner to signal start. 
```
