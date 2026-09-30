# [?] Fix stack overflow caused by use of `poll_nonblocking()` which was

## Summary
Severity: Unknown
Chain: Monad
Component: category-labs/monad
Published: 2023-11-08
Source: https://github.com/category-labs/monad/commit/d494e9dec689d4817adf1f5b8ca1a0717ff9f7de
Type: security-commit

## Details
Fix stack overflow caused by use of `poll_nonblocking()` which was
unaware of deferred initiation.

## Patch
### db/include/monad/async/io.hpp
```diff
@@ -171,6 +171,14 @@ class AsyncIO final
         }
         return n;
     }
+    std::optional<size_t>
+    poll_blocking_if_not_within_completions(size_t count = 1)
+    {
+        if (detail::AsyncIO_per_thread_state().am_within_completions()) {
+            return std::nullopt;
+        }
+        return poll_blocking(count);
+    }
 
     // Never blocks
     size_t poll_nonblocking(size_t count = size_t(-1))
@@ -183,6 +191,14 @@ class AsyncIO final
         }
         return n;
     }
+    std::optional<size_t>
+    poll_nonblocking_if_not_within_completions(size_t count = size_t(-1))
+    {
+        if (detail::AsyncIO_per_thread_state().am_within_completions()) {
+            return std::nullopt;
+        }
+        return poll_nonblocking(count);
+    }
 
     void wait_until_done()
     {
```

### db/src/monad/async/test/io.cpp
```diff
@@ -1,6 +1,6 @@
 #include "gtest/gtest.h"
 
-#include "monad/async/io.hpp"
+#include "monad/async/io_senders.hpp"
 
 namespace
 {
@@ -29,4 +29,77 @@ namespace
             }
         }
     }
+
+    struct poll_does_not_recurse_receiver_t
+    {
+        static constexpr bool lifetime_managed_internally = false;
+
+        int &count, &recursion_count, &max_recursion_count;
+        std::vector<std::unique_ptr<monad::async::erased_connected_operation>>
+            &states;
+
+        inline void set_value(
+            monad::async::erased_connected_operation *,
+            monad::async::result<void>);
+    };
+    TEST(AsyncIO, poll_does_not_recurse)
+    {
+        int count = 1000000;
+        int recursion_count = 0, max_recursion_count = 0;
+        monad::async::storage_pool pool(
+            monad::async::use_anonymous_inode_tag{});
+        monad::io::Ring testring(128, 0);
+        monad::io::Buffers testrwbuf{
+            testring, 1, 1, monad::async::AsyncIO::MONAD_IO_BUFFERS_READ_SIZE};
+        monad::async::AsyncIO testio(pool, testring, testrwbuf);
+        std::vector<std::unique_ptr<monad::async::erased_connected_operation>>
+            states;
+        states.reserve(size_t(count));
+        for (size_t n = 0; n < 1000; n++) {
+            std::unique_ptr<monad::async::erased_connected_operation> state(
+                new auto( // NOLINT
+                    monad::async::connect(
+                        testio,
+                        monad::async::timed_delay_sender(
+                            std::chrono::seconds(0)),
+                        poll_does_not_recurse_receiver_t{
+                            count,
+                            recursion_count,
+                            max_recursion_count,
+                            states})));
+            state->initiate();
+            states.push_back(std::move(state));
+        }
+        testio.wait_until_done();
+        std::cout << "At worst " << max_recursion_count
+                  << " recursions on stack occurred." << std::endl;
+        EXPECT_LT(max_recursion_count, 2);
+    }
+    inline void poll_does_not_recurse_receiver_t::set_value(
+        monad::async::erased_connected_operation *iostate,
+        monad::async::result<void> res)
+    {
+        MONAD_ASSERT(res);
+        if (++recursion_count > max_recursion_count) {
+            max_recursion_count = recursion_count;
+        }
+        if (--count > 0) {
+            auto &io = *iostate->executor();
+            std::unique_ptr<monad::async::erased_connected_operation> state(
+                new auto( // NOLINT
+                    monad::async::connect(
+                        io,
+                        monad::async::timed_delay_sender(
+                            std::chrono::seconds(0)),
+                        poll_does_not_recurse_receiver_t{
+                            count,
+                            recursion_count,
+                            max_recursion_count,
+                            states})));
+            state->initiate();
+            states.push_back(std::move(state));
+            io.poll_nonblocking_if_not_within_completions(1);
+        }
+        --recursion_count;
+    }
 }
```

### db/src/monad/mpt/trie.cpp
```diff
@@ -962,7 +962,7 @@ node_writer_unique_ptr_type replace_node_writer(
 async_write_node_result async_write_node(UpdateAux &aux, Node *node)
 {
     node_writer_unique_ptr_type &node_writer = aux.node_writer;
-    aux.io->poll_nonblocking(1);
+    aux.io->poll_nonblocking_if_not_within_completions(1);
     auto *sender = &node_writer->sender();
     auto const size = node->disk_size;
     auto const remaining_bytes = sender->remaining_buffer_bytes();
```
