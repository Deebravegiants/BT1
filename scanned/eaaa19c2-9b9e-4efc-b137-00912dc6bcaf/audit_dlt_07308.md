# [?] Prevent DatabaseRotateImp crash on shutdown (RIPD-1392):

## Summary
Severity: Unknown
Chain: XRP
Component: XRPLF/rippled
Published: 2017-02-14
Source: https://github.com/XRPLF/rippled/commit/1d482eeecb3c568e748940c19b5d9967320aa091
Type: security-commit

## Details
Prevent DatabaseRotateImp crash on shutdown (RIPD-1392):

The DatabaseImp holds threads that access DatabaseRotateImp.  But
the DatabaseRotateImp's destructor runs before the DatabaseImp
destructor.  The DatabaseRotateImp now assures that the
DatabaseImp threads are stopped before the DatabaseRotateImp
destructor completes.

## Patch
### src/ripple/nodestore/impl/DatabaseImp.h
```diff
@@ -92,17 +92,15 @@ class DatabaseImp
             fdlimit_ = m_backend->fdlimit();
     }
 
-    ~DatabaseImp ()
+    ~DatabaseImp () override
     {
-        {
-            std::lock_guard <std::mutex> lock (m_readLock);
-            m_readShut = true;
-            m_readCondVar.notify_all ();
-            m_readGenCondVar.notify_all ();
-        }
-
-        for (auto& e : m_readThreads)
-            e.join();
+        // NOTE!
+        // Any derived class should call the stopThreads() method in its
+        // destructor.  Otherwise, occasionally, the derived class may
+        // crash during shutdown when its members are accessed by one of
+        // these threads after the derived class is destroyed but before
+        // this base class is destroyed.
+        stopThreads();
     }
 
     std::string
@@ -442,6 +440,23 @@ class DatabaseImp
         return fdlimit_;
     }
 
+protected:
+    void stopThreads ()
+    {
+        {
+            std::lock_guard <std::mutex> lock (m_readLock);
+            if (m_readShut) // Only stop threads once.
+                return;
+
+            m_readShut = true;
+            m_readCondVar.notify_all ();
+            m_readGenCondVar.notify_all ();
+        }
+
+        for (auto& e : m_readThreads)
+            e.join();
+    }
+
 private:
     std::atomic <std::uint32_t> m_storeCount;
     std::atomic <std::uint32_t> m_fetchTotalCount;
```

### src/ripple/nodestore/impl/DatabaseRotatingImp.h
```diff
@@ -63,6 +63,12 @@ class DatabaseRotatingImp
             , archiveBackend_ (archiveBackend)
     {}
 
+    ~DatabaseRotatingImp () override
+    {
+        // Stop threads before data members are destroyed.
+        DatabaseImp::stopThreads ();
+    }
+
     std::shared_ptr <Backend> const& getWritableBackend() const override
     {
         std::lock_guard <std::mutex> lock (rotateMutex_);
```
