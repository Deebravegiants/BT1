# [?] Fix logging deadlock

## Summary
Severity: Unknown
Chain: Monero
Component: monero-project/monero
Published: 2025-11-08
Source: https://github.com/monero-project/monero/commit/c01e1fa288bbf52a9d5c860d6dfc392cc0548319
Type: security-commit

## Details
Fix logging deadlock

## Patch
### contrib/epee/include/misc_log_ex.h
```diff
@@ -30,6 +30,7 @@
 
 #ifdef __cplusplus
 
+#include <sstream>
 #include <string>
 
 #include "easylogging++.h"
@@ -40,9 +41,15 @@
 #define MAX_LOG_FILE_SIZE 104850000 // 100 MB - 7600 bytes
 #define MAX_LOG_FILES 10
 
+#define LOG_TO_STRING(x) \
+    std::stringstream ss; \
+    ss << x; \
+    const std::string str = ss.str();
+
 #define MCLOG_TYPE(level, cat, color, type, x) do { \
     if (el::Loggers::allowed(level, cat)) { \
-      el::base::Writer(level, color, __FILE__, __LINE__, ELPP_FUNC, type).construct(cat) << x; \
+      LOG_TO_STRING(x); \
+      el::base::Writer(level, color, __FILE__, __LINE__, ELPP_FUNC, type).construct(cat) << str; \
     } \
   } while (0)
 
@@ -91,7 +98,8 @@
   do { \
     if (el::Loggers::allowed(level, cat)) { \
       init; \
-      el::base::Writer(level, color, __FILE__, __LINE__, ELPP_FUNC, type).construct(cat) << x; \
+      LOG_TO_STRING(x); \
+      el::base::Writer(level, color, __FILE__, __LINE__, ELPP_FUNC, type).construct(cat) << str; \
     } \
   } while(0)
 #define MIDEBUG(init, x) IFLOG(el::Level::Debug, MONERO_DEFAULT_LOG_CATEGORY, el::Color::Default, el::base::DispatchAction::NormalLog, init, x)
```

### external/easylogging++/easylogging++.cc
```diff
@@ -3065,8 +3065,9 @@ void Writer::triggerDispatch(void) {
   }
   if (m_proceed && m_level == Level::Fatal
       && !ELPP->hasFlag(LoggingFlag::DisableApplicationAbortOnFatalLog)) {
+    const std::string str = "Aborting application. Reason: Fatal log at [" + std::string(m_file) + ":" + std::to_string(m_line) + "]";
     base::Writer(Level::Warning, Color::Default, m_file, m_line, m_func).construct(1, base::consts::kDefaultLoggerId)
-        << "Aborting application. Reason: Fatal log at [" << m_file << ":" << m_line << "]";
+        << str;
     std::stringstream reasonStream;
     reasonStream << "Fatal log at [" << m_file << ":" << m_line << "]"
                  << " If you wish to disable 'abort on fatal log' please use "
```

### external/easylogging++/easylogging++.h
```diff
@@ -3275,9 +3275,7 @@ class Writer : base::NoCopy {
     processDispatch();
   }
 
-  template <typename T>
-  inline typename std::enable_if<std::is_integral<T>::value, Writer&>::type
-  operator<<(T log) {
+  Writer& operator<<(const std::string &log) {
 #if ELPP_LOGGING_ENABLED
   if (m_proceed) {
     m_messageBuilder << log;
@@ -3286,26 +3284,6 @@ class Writer : base::NoCopy {
   return *this;
   }
 
-  template <typename T>
-  inline typename std::enable_if<!std::is_integral<T>::value, Writer&>::type
-  operator<<(const T& log) {
-#if ELPP_LOGGING_ENABLED
-    if (m_proceed) {
-      m_messageBuilder << log;
-    }
-#endif  // ELPP_LOGGING_ENABLED
-    return *this;
-  }
-
-  inline Writer& operator<<(std::ostream& (*log)(std::ostream&)) {
-#if ELPP_LOGGING_ENABLED
-    if (m_proceed) {
-      m_messageBuilder << log;
-    }
-#endif  // ELPP_LOGGING_ENABLED
-    return *this;
-  }
-
   inline operator bool() {
     return true;
   }
@@ -3622,8 +3600,9 @@ class DefaultPerformanceTrackingCallback : public PerformanceTrackingCallback {
         ss << ELPP_LITERAL("]");
       }
     }
+    const std::string str = ss.str();
     el::base::Writer(m_data->performanceTracker()->level(), m_data->file(), m_data->line(), m_data->func()).construct(1,
-        m_data->loggerId().c_str()) << ss.str();
+        m_data->loggerId().c_str()) << str;
   }
  private:
   const PerformanceTrackingData* m_data;
```

### src/cryptonote_protocol/cryptonote_protocol_handler.inl
```diff
@@ -48,6 +48,7 @@
 #include "net/network_throttle-detail.hpp"
 #include "common/pruning.h"
 #include "common/util.h"
+#include "misc_log_ex.h"
 
 #undef MONERO_DEFAULT_LOG_CATEGORY
 #define MONERO_DEFAULT_LOG_CATEGORY "net.cn"
@@ -59,8 +60,10 @@
     const char *cat = "net.p2p.msg"; \
     if (ELPP->vRegistry()->allowed(level, cat)) { \
       init; \
-      if (test) \
-        el::base::Writer(level, el::Color::Default, __FILE__, __LINE__, ELPP_FUNC, el::base::DispatchAction::NormalLog).construct(cat) << x; \
+      if (test) { \
+        LOG_TO_STRING(x); \
+        el::base::Writer(level, el::Color::Default, __FILE__, __LINE__, ELPP_FUNC, el::base::DispatchAction::NormalLog).construct(cat) << str; \
+      } \
     } \
   } while(0)
 
```

### tests/unit_tests/logging.cpp
```diff
@@ -28,6 +28,10 @@
 //
 // Parts of this file are originally copyright (c) 2012-2013 The Cryptonote developers
 
+#include <condition_variable>
+#include <mutex>
+#include <thread>
+
 #include <boost/filesystem.hpp>
 #include "gtest/gtest.h"
 #include "file_io_utils.h"
@@ -251,3 +255,55 @@ TEST(logging, empty_configuration)
     EXPECT_NO_THROW(log1.configure(cfg));
     EXPECT_EQ(log1.typedConfigurations()->filename(el::Level::Info), "");
 }
+
+TEST(logging, deadlock)
+{
+  std::mutex inner_mutex;
+
+  // 1. Thread 1 starts logger
+  // 2. Thread 2 grabs inner mutex shared across threads
+  // 3. Thread 2 logs
+  // 4. Thread 1 grabs inner mutex shared across threads
+  // 5. Thread 1 finishes logging
+  std::condition_variable cv1, cv2;
+  std::mutex mutex1, mutex2;
+  std::unique_lock<std::mutex> lock_until_t1_starts_logger(mutex1);
+  std::unique_lock<std::mutex> lock_until_t2_finishes_logging(mutex2);
+  bool t1_started_logger = false;
+  bool t2_finished_logging = false;
+
+  const auto thread1_func = [&]
+  {
+    const auto thread1_inner_func = [&]() -> std::string
+    {
+      t1_started_logger = true;
+      lock_until_t1_starts_logger.unlock();
+      cv1.notify_one();
+      cv2.wait(lock_until_t2_finishes_logging, [&]{return t2_finished_logging;});
+
+      std::lock_guard<std::mutex> guard(inner_mutex);
+      return "world!";
+    };
+    MGINFO("Hello, " << thread1_inner_func() << " - Sincerely, thread 1");
+  };
+
+  const auto thread2_func = [&]
+  {
+    cv1.wait(lock_until_t1_starts_logger, [&]{return t1_started_logger;});
+
+    {
+      std::lock_guard<std::mutex> guard(inner_mutex);
+      MGINFO("Hello, world! - Sincerely, thread 2");
+    }
+
+    t2_finished_logging = true;
+    lock_until_t2_finishes_logging.unlock();
+    cv2.notify_one();
+  };
+
+  std::thread t1(thread1_func);
+  std::thread t2(thread2_func);
+
+  t1.join();
+  t2.join();
+}
```
