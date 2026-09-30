# [?] Merge #13148: logging: Fix potential use-after-free in LogPrintStr(...)

## Summary
Severity: Unknown
Chain: Bitcoin Cash
Component: bitcoin-cash-node/bitcoin-cash-node
Published: 2018-05-03
Source: https://github.com/bitcoin-cash-node/bitcoin-cash-node/commit/1d91c62d1401d3dee711283a71423f2fb23f61c6
Type: security-commit

## Details
Merge #13148: logging: Fix potential use-after-free in LogPrintStr(...)

Summary:
0bd4cd3 logging: remove unused return value from LogPrintStr (practicalswift)
76f344d logging: Fix potential use-after-free in LogPrintStr(...) (practicalswift)

Pull request description:

  Fix potential use-after-free in `LogPrintStr(...)`.

  `freopen(…)` frees `m_fileout`.

Tree-SHA512: ceee1f659c10a21525aa648377afeea0a37016339f5269dea54850ba3b475aa316f4931081655717b65f981598fdc9d79a1e79e55f7084c242eeb7bf372bc4b6

Backport of Core PR13148
https://github.com/bitcoin/bitcoin/pull/13148/

Test Plan:
  make check

Reviewers: deadalnix, Fabien, jasonbcox, O1 Bitcoin ABC, #bitcoin_abc

Reviewed By: deadalnix, O1 Bitcoin ABC, #bitcoin_abc

Differential Revision: https://reviews.bitcoinabc.org/D3976

## Patch
### src/logging.cpp
```diff
@@ -164,38 +164,35 @@ std::string BCLog::Logger::LogTimestampStr(const std::string &str) {
     return strStamped;
 }
 
-int BCLog::Logger::LogPrintStr(const std::string &str) {
-    // Returns total number of characters written.
-    int ret = 0;
-
+void BCLog::Logger::LogPrintStr(const std::string &str) {
     std::string strTimestamped = LogTimestampStr(str);
 
     if (m_print_to_console) {
         // Print to console.
-        ret = fwrite(strTimestamped.data(), 1, strTimestamped.size(), stdout);
+        fwrite(strTimestamped.data(), 1, strTimestamped.size(), stdout);
         fflush(stdout);
     } else if (m_print_to_file) {
         std::lock_guard<std::mutex> scoped_lock(m_file_mutex);
 
         // Buffer if we haven't opened the log yet.
         if (m_fileout == nullptr) {
-            ret = strTimestamped.length();
             m_msgs_before_open.push_back(strTimestamped);
         } else {
             // Reopen the log file, if requested.
             if (m_reopen_file) {
                 m_reopen_file = false;
                 fs::path pathDebug = GetDebugLogPath();
-                if (fsbridge::freopen(pathDebug, "a", m_fileout) != nullptr) {
-                    // unbuffered.
-                    setbuf(m_fileout, nullptr);
+                m_fileout = fsbridge::freopen(pathDebug, "a", m_fileout);
+                if (!m_fileout) {
+                    return;
                 }
+                // unbuffered.
+                setbuf(m_fileout, nullptr);
             }
 
-            ret = FileWriteStr(strTimestamped, m_fileout);
+            FileWriteStr(strTimestamped, m_fileout);
         }
     }
-    return ret;
 }
 
 void BCLog::Logger::ShrinkDebugFile() {
```

### src/logging.h
```diff
@@ -83,7 +83,7 @@ class Logger {
     ~Logger();
 
     /** Send a string to the log output */
-    int LogPrintStr(const std::string &str);
+    void LogPrintStr(const std::string &str);
 
     fs::path GetDebugLogPath();
     bool OpenDebugLog();
```
