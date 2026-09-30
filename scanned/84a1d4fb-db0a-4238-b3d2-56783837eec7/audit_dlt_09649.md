# [?] Fix CCheckQueue IsIdle (potential) race condition and remove dangerous constructors.

## Summary
Severity: Unknown
Chain: Dogecoin
Component: dogecoin/dogecoin
Published: 2017-01-09
Source: https://github.com/dogecoin/dogecoin/commit/e2073424fd5a185781750347fbfbb0c108ef66fd
Type: security-commit

## Details
Fix CCheckQueue IsIdle (potential) race condition and remove dangerous constructors.

## Patch
### src/checkqueue.h
```diff
@@ -127,6 +127,9 @@ class CCheckQueue
     }
 
 public:
+    //! Mutex to ensure only one concurrent CCheckQueueControl
+    boost::mutex ControlMutex;
+
     //! Create a new check queue
     CCheckQueue(unsigned int nBatchSizeIn) : nIdle(0), nTotal(0), fAllOk(true), nTodo(0), fQuit(false), nBatchSize(nBatchSizeIn) {}
 
@@ -161,12 +164,6 @@ class CCheckQueue
     {
     }
 
-    bool IsIdle()
-    {
-        boost::unique_lock<boost::mutex> lock(mutex);
-        return (nTotal == nIdle && nTodo == 0 && fAllOk == true);
-    }
-
 };
 
 /** 
@@ -177,16 +174,18 @@ template <typename T>
 class CCheckQueueControl
 {
 private:
-    CCheckQueue<T>* pqueue;
+    CCheckQueue<T> * const pqueue;
     bool fDone;
 
 public:
-    CCheckQueueControl(CCheckQueue<T>* pqueueIn) : pqueue(pqueueIn), fDone(false)
+    CCheckQueueControl() = delete;
+    CCheckQueueControl(const CCheckQueueControl&) = delete;
+    CCheckQueueControl& operator=(const CCheckQueueControl&) = delete;
+    explicit CCheckQueueControl(CCheckQueue<T> * const pqueueIn) : pqueue(pqueueIn), fDone(false)
     {
         // passed queue is supposed to be unused, or NULL
         if (pqueue != NULL) {
-            bool isIdle = pqueue->IsIdle();
-            assert(isIdle);
+            ENTER_CRITICAL_SECTION(pqueue->ControlMutex);
         }
     }
 
@@ -209,6 +208,9 @@ class CCheckQueueControl
     {
         if (!fDone)
             Wait();
+        if (pqueue != NULL) {
+            LEAVE_CRITICAL_SECTION(pqueue->ControlMutex);
+        }
     }
 };
 
```
