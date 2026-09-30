# [?] easylogging++: fix crash with reentrant logging

## Summary
Severity: Unknown
Chain: Monero
Component: monero-project/monero
Published: 2020-07-29
Source: https://github.com/monero-project/monero/commit/92e6b7df2c816dc4b0a075b0d2fafbc5dc018bbb
Type: security-commit

## Details
easylogging++: fix crash with reentrant logging

## Patch
### external/easylogging++/easylogging++.cc
```diff
@@ -2968,6 +2968,16 @@ void Writer::initializeLogger(Logger *logger, bool needLock) {
 }
 
 void Writer::processDispatch() {
+  static std::atomic_flag in_dispatch;
+  if (in_dispatch.test_and_set())
+  {
+    if (m_proceed && m_logger != NULL)
+    {
+      m_logger->stream().str(ELPP_LITERAL(""));
+      m_logger->releaseLock();
+    }
+    return;
+  }
 #if ELPP_LOGGING_ENABLED
   if (ELPP->hasFlag(LoggingFlag::MultiLoggerSupport)) {
     bool firstDispatched = false;
@@ -3006,6 +3016,7 @@ void Writer::processDispatch() {
     m_logger->releaseLock();
   }
 #endif // ELPP_LOGGING_ENABLED
+  in_dispatch.clear();
 }
 
 void Writer::triggerDispatch(void) {
```
