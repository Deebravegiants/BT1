# [?] fix crash on shutdown when e.g. changing -txindex and abort action

## Summary
Severity: Unknown
Chain: Dogecoin
Component: dogecoin/dogecoin
Published: 2015-06-15
Source: https://github.com/dogecoin/dogecoin/commit/a46370f7917fea7210d85c7a594642fb9d93a0ea
Type: security-commit

## Details
fix crash on shutdown when e.g. changing -txindex and abort action

- fixes #3136
- the problem is related to Boost path and a static initialized internal
  pointer
- using a std::string in CDBEnv::EnvShutdown() prevents the problem
- this removes the boost::filesystem::path path field from CDBEnv

Github-Pull: #6282
Rebased-From: 0ce30eaa36295447c6e7f8d16a05798c746fe28a

## Patch
### src/wallet/db.cpp
```diff
@@ -43,7 +43,7 @@ void CDBEnv::EnvShutdown()
     if (ret != 0)
         LogPrintf("CDBEnv::EnvShutdown: Error %d shutting down database environment: %s\n", ret, DbEnv::strerror(ret));
     if (!fMockDb)
-        DbEnv(0).remove(path.string().c_str(), 0);
+        DbEnv(0).remove(strPath.c_str(), 0);
 }
 
 void CDBEnv::Reset()
@@ -78,10 +78,10 @@ bool CDBEnv::Open(const boost::filesystem::path& pathIn)
 
     boost::this_thread::interruption_point();
 
-    path = pathIn;
-    boost::filesystem::path pathLogDir = path / "database";
+    strPath = pathIn.string();
+    boost::filesystem::path pathLogDir = pathIn / "database";
     TryCreateDirectory(pathLogDir);
-    boost::filesystem::path pathErrorFile = path / "db.log";
+    boost::filesystem::path pathErrorFile = pathIn / "db.log";
     LogPrintf("CDBEnv::Open: LogDir=%s ErrorFile=%s\n", pathLogDir.string(), pathErrorFile.string());
 
     unsigned int nEnvFlags = 0;
@@ -98,7 +98,7 @@ bool CDBEnv::Open(const boost::filesystem::path& pathIn)
     dbenv->set_flags(DB_AUTO_COMMIT, 1);
     dbenv->set_flags(DB_TXN_WRITE_NOSYNC, 1);
     dbenv->log_set_config(DB_LOG_AUTO_REMOVE, 1);
-    int ret = dbenv->open(path.string().c_str(),
+    int ret = dbenv->open(strPath.c_str(),
                          DB_CREATE |
                              DB_INIT_LOCK |
                              DB_INIT_LOG |
@@ -455,7 +455,7 @@ void CDBEnv::Flush(bool fShutdown)
                 dbenv->log_archive(&listp, DB_ARCH_REMOVE);
                 Close();
                 if (!fMockDb)
-                    boost::filesystem::remove_all(path / "database");
+                    boost::filesystem::remove_all(boost::filesystem::path(strPath) / "database");
             }
         }
     }
```

### src/wallet/db.h
```diff
@@ -27,7 +27,9 @@ class CDBEnv
 private:
     bool fDbEnvInit;
     bool fMockDb;
-    boost::filesystem::path path;
+    // Don't change into boost::filesystem::path, as that can result in
+    // shutdown problems/crashes caused by a static initialized internal pointer.
+    std::string strPath;
 
     void EnvShutdown();
 
```
