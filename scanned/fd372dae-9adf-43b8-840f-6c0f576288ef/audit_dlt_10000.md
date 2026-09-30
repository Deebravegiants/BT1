# [?] Prevent use-after-free in `read_buffer_exhaustion_causes_death`

## Summary
Severity: Unknown
Chain: Monad
Component: category-labs/monad
Published: 2024-03-29
Source: https://github.com/category-labs/monad/commit/6bfabb26552817736ac9fd1010988e5120186647
Type: security-commit

## Details
Prevent use-after-free in `read_buffer_exhaustion_causes_death`
death test, and memory leak in `write_buffer_exhaustion_causes_death`.

## Patch
### db/src/monad/async/test/io_death.cpp
```diff
@@ -24,8 +24,6 @@ namespace
 {
     TEST(AsyncIODeathTest, write_buffer_exhaustion_causes_death)
     {
-        // It complains about there being two threads without this, despite the
-        // fact that very clearly there is exactly one thread and gdb agrees.
         testing::FLAGS_gtest_death_test_style = "threadsafe";
 
         monad::async::storage_pool pool(
@@ -40,6 +38,9 @@ namespace
                 monad::async::AsyncIO::MONAD_IO_BUFFERS_READ_SIZE,
                 monad::async::AsyncIO::MONAD_IO_BUFFERS_WRITE_SIZE);
         monad::async::AsyncIO testio(pool, testrwbuf);
+        std::vector<monad::async::erased_connected_operation_ptr> states;
+        auto empty_testio = monad::make_scope_exit(
+            [&]() noexcept { testio.wait_until_done(); });
 
         struct empty_receiver
         {
@@ -60,7 +61,7 @@ namespace
                 // Exactly the same test as the non-death test, except for this
                 // line
                 // state->initiate();
-                state.release();
+                states.push_back(std::move(state));
             };
             if (n > 0) {
                 EXPECT_EXIT(make(), ::testing::KilledBySignal(SIGABRT), ".*");
@@ -73,8 +74,6 @@ namespace
 
     TEST(AsyncIODeathTest, read_buffer_exhaustion_causes_death)
     {
-        // It complains about there being two threads without this, despite the
-        // fact that very clearly there is exactly one thread and gdb agrees.
         testing::FLAGS_gtest_death_test_style = "threadsafe";
 
         monad::async::storage_pool pool(
@@ -89,6 +88,8 @@ namespace
             monad::async::AsyncIO::MONAD_IO_BUFFERS_WRITE_SIZE);
         monad::async::AsyncIO testio(pool, testrwbuf);
         std::vector<monad::async::read_single_buffer_sender::buffer_type> bufs;
+        auto empty_testio = monad::make_scope_exit(
+            [&]() noexcept { testio.wait_until_done(); });
 
         struct empty_receiver
         {
```
