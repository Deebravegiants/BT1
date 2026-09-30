# [?] [core] Fix out-of-bounds read and vacuous checks in log_ffi_test

## Summary
Severity: Unknown
Chain: Monad
Component: category-labs/monad
Published: 2026-09-28
Source: https://github.com/category-labs/monad/commit/4f49e7a5510bb0bf66169dfa633b7a79b8fa329d
Type: security-commit

## Details
[core] Fix out-of-bounds read and vacuous checks in log_ffi_test

monad_log::message is not null-terminated, but capture_log copied
exactly message_len bytes and the test printed the copy as a C string,
so strlen read past the end and ASAN reports a heap-buffer-overflow.
The copy was also allocated with new[] and released with free().

The message checks could not fail. The callback receives the whole
formatted log line, timestamp first, so strncmp against the logged text
differed at the first byte and EXPECT_TRUE(strncmp(...)) always held.

Capture the message into a std::string and check that the line ends
with the logged text. Also destroy the handler, which the test leaked.

The callback runs on the quill backend thread, and sleeping did not
order its writes before the test's reads, so TSAN reports a data race.
Wait with flush_logger() instead, which blocks until the backend has
processed every earlier message.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>

## Patch
### category/core/log_ffi_test.cpp
```diff
@@ -16,37 +16,34 @@
 #include <category/core/log.hpp>
 #include <category/core/log_ffi.h>
 
-#include <bit>
-#include <chrono>
 #include <cstdint>
 #include <print>
-#include <thread>
-
-#include <stdlib.h>
-#include <string.h>
+#include <string>
 
 #include <gtest/gtest.h>
 
+struct CapturedLog
+{
+    uint8_t syslog_level;
+    std::string message;
+};
+
 static void capture_log(monad_log const *const input_log, uintptr_t const ptr)
 {
     // The "logging" function makes a copy of the `monad_log` object, to be
     // tested after the logging completes; we also copy the message's string
     // buffer, since the logging framework may destroy it after this returns
-    monad_log *const output_log = std::bit_cast<monad_log *>(ptr);
-    *output_log = *input_log;
-    if (output_log->message != nullptr) {
-        char *output_message = new char[output_log->message_len];
-        memcpy(output_message, output_log->message, output_log->message_len);
-        output_log->message = output_message;
-    }
+    CapturedLog *const output_log = reinterpret_cast<CapturedLog *>(ptr);
+    output_log->syslog_level = input_log->syslog_level;
+    output_log->message.assign(input_log->message, input_log->message_len);
 }
 
 TEST(LogFFI, Basic)
 {
     constexpr uint8_t SYSLOG_ERR = 3;
     constexpr uint8_t SYSLOG_WARN = 4;
     monad_log_handler *handler;
-    monad_log output = {};
+    CapturedLog output = {};
 
     ASSERT_EQ(
         0,
@@ -55,50 +52,36 @@ TEST(LogFFI, Basic)
             "test_handler",
             capture_log,
             nullptr,
-            std::bit_cast<uintptr_t>(&output)));
+            reinterpret_cast<uintptr_t>(&output)));
     ASSERT_EQ(0, monad_log_init(&handler, 1, SYSLOG_WARN));
 
 // A macro because it has to be literal, not even constexpr
 #define FIRST_ERROR "First error"
     LOG_ERROR(FIRST_ERROR);
-
-    // Give the quill background thread ample time to drain the log queue,
-    // only then will the `capture_log` callback above be run; we wait a
-    // whole second because the time to warm up this thread is quite long
-    std::this_thread::sleep_for(std::chrono::seconds{1});
+    monad::flush_logger();
 
     EXPECT_EQ(SYSLOG_ERR, output.syslog_level);
-    ASSERT_NE(nullptr, output.message);
-    EXPECT_TRUE(strncmp(FIRST_ERROR, output.message, sizeof FIRST_ERROR));
+    EXPECT_TRUE(output.message.ends_with(FIRST_ERROR "\n"));
 
     std::print(stderr, "First log message is: {}", output.message);
-    free(const_cast<char *>(output.message));
     output = {};
 
 #define SECOND_ERROR "Second error"
     LOG_ERROR(SECOND_ERROR);
-
-    // Recording happens at much more interactive rates once the background
-    // thread is warmed up; we make that thread aggressively sleep to avoid
-    // wasting CPU resources, but even so this wait number _could_ be much
-    // lower. We keep it unrealistically high so that the test won't fail
-    // intermittently in the CI even when the system is under extreme
-    // scheduling pressure
-    std::this_thread::sleep_for(std::chrono::milliseconds{100});
+    monad::flush_logger();
 
     EXPECT_EQ(SYSLOG_ERR, output.syslog_level);
-    ASSERT_NE(nullptr, output.message);
-    EXPECT_TRUE(strncmp(SECOND_ERROR, output.message, sizeof SECOND_ERROR));
+    EXPECT_TRUE(output.message.ends_with(SECOND_ERROR "\n"));
 
     std::print(stderr, "Second log message is: {}", output.message);
-    free(const_cast<char *>(output.message));
     output = {};
 
     LOG_INFO("Hello, world");
-    std::this_thread::sleep_for(std::chrono::milliseconds{100});
+    monad::flush_logger();
 
     // Because we initialized with SYSLOG_WARN, LOG_INFO won't do anything
     EXPECT_EQ(0, output.syslog_level);
-    EXPECT_EQ(nullptr, output.message);
-    EXPECT_EQ(0, output.message_len);
+    EXPECT_TRUE(output.message.empty());
+
+    monad_log_handler_destroy(handler);
 }
```
