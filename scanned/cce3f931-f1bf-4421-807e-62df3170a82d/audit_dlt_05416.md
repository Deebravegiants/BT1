# [?] [event] fix race condition in event ring create

## Summary
Severity: Unknown
Chain: Monad
Component: monad-crypto/monad
Published: 2025-11-14
Source: https://github.com/category-labs/monad/commit/41fbfc128a7a5a9e6cd3c8512dff2d3110dc3aea
Type: security-commit

## Details
[event] fix race condition in event ring create

Currently, nothing about an event ring indicates whether the file is
properly initialized or not. A race exists where consumers can try
to mmap a partially-initialized file, and get strange errors. The new
"more robust" blockcap daemon (blockcapd) encountered this.

This commit solves the issue, using a file system atomic operation
provided by the kernel. Now a user will never see a partial file but
could still see a truncated (to zero) file.

The long comment at the top of `create_owned_event_ring` explains how
it works.

## Patch
### cmd/monad/event.cpp
```diff
@@ -27,17 +27,19 @@
 #include <concepts>
 #include <cstdint>
 #include <expected>
+#include <filesystem>
 #include <format>
 #include <memory>
 #include <ranges>
 #include <string>
 #include <string_view>
 #include <system_error>
-#include <tuple>
 #include <vector>
 
 #include <errno.h>
 #include <fcntl.h>
+#include <signal.h>
+#include <stdio.h>
 #include <string.h>
 #include <sys/file.h>
 #include <sys/mman.h>
@@ -46,6 +48,8 @@
 #include <quill/LogLevel.h>
 #include <quill/Quill.h>
 
+namespace fs = std::filesystem;
+
 MONAD_ANONYMOUS_NAMESPACE_BEGIN
 
 template <std::integral I>
@@ -66,6 +70,219 @@ std::string try_parse_int_token(std::string_view s, I *i)
     return {};
 }
 
+// Create event ring files with rw-rw-r--
+constexpr mode_t CreateMode = S_IRUSR | S_IWUSR | S_IRGRP | S_IWGRP | S_IROTH;
+
+int claim_event_ring_file(
+    int const dir_fd, char const *const file_name, char const *const full_path,
+    int *const ring_fd)
+{
+    *ring_fd = openat(dir_fd, file_name, O_RDONLY | O_CREAT, CreateMode);
+    if (*ring_fd == -1) {
+        int const rc = errno;
+        LOG_ERROR(
+            "openat failed for event ring file `{}`: {} [{}]",
+            full_path,
+            strerror(rc),
+            rc);
+        return rc;
+    }
+    if (flock(*ring_fd, LOCK_EX | LOCK_NB) == -1) {
+        int const saved_errno = errno;
+        if (saved_errno == EWOULDBLOCK) {
+            pid_t owner_pid = 0;
+            size_t owner_pid_size = 1;
+
+            // Another process has an exclusive lock; find out who it is
+            (void)monad_event_ring_find_writer_pids(
+                *ring_fd, &owner_pid, &owner_pid_size);
+            if (owner_pid == 0) {
+                LOG_ERROR(
+                    "event ring file `{}` is owned by an unknown other process",
+                    full_path);
+            }
+            else {
+                LOG_ERROR(
+                    "event ring file `{}` is owned by pid {}",
+                    full_path,
+                    owner_pid);
+            }
+            return saved_errno;
+        }
+        LOG_ERROR(
+            "flock on event ring file `{}` failed: {} ({})",
+            full_path,
+            strerror(saved_errno),
+            saved_errno);
+        return saved_errno;
+    }
+    // Note: truncate(2) not ftruncate(2), because we deliberately opened the
+    // fd with O_RDONLY; even though we're going to destroy this file soon
+    // anyway, we explicitly truncate to zero so that space-constrained
+    // filesystems like hugetlbfs can drop the committed pages if they're not
+    // mapped anywhere. We will initialize the replacement for this file before
+    // destroying it, so for a moment both will exist.
+    if (truncate(full_path, 0) == -1) {
+        int const saved_errno = errno;
+        LOG_ERROR(
+            "truncate to zero failed for event ring file `{}` ({})",
+            full_path,
+            strerror(saved_errno),
+            saved_errno);
+        return saved_errno;
+    }
+    return 0;
+}
+
+int allocate_event_ring_file(
+    monad_event_ring_simple_config const *const simple_cfg, int const dir_fd,
+    char const *const file_name, char const *const full_path,
+    int *const init_ring_fd)
+{
+    *init_ring_fd =
+        openat(dir_fd, file_name, O_RDWR | O_CREAT | O_EXCL, CreateMode);
+    if (*init_ring_fd == -1) {
+        int const rc = errno;
+        LOG_ERROR(
+            "could not create event ring temporary initialization file `{}` "
+            "(for {}): "
+            "{} [{}]",
+            file_name,
+            full_path,
+            strerror(rc),
+            rc);
+        return rc;
+    }
+    if (flock(*init_ring_fd, LOCK_EX) == -1) {
+        int const saved_errno = errno;
+        LOG_ERROR(
+            "flock on event ring file temporary initialization file `{}` (for "
+            "{}) failed: {} ({})",
+            file_name,
+            full_path,
+            strerror(saved_errno),
+            saved_errno);
+        return saved_errno;
+    }
+    if (int const rc = monad_event_ring_init_simple(
+            simple_cfg, *init_ring_fd, 0, full_path)) {
+        LOG_ERROR(
+            "event library error -- {}", monad_event_ring_get_last_error());
+        return rc;
+    }
+    return 0;
+}
+
+// Create an event ring file which we own exclusively. This is tricky because
+// as soon as we open a file with O_RDWR or O_WRONLY, any API user calling the
+// function monad_event_ring_find_writer_pids might assume the file is ready
+// to be used. Unless they're careful, they could mmap a half-initialized file,
+// which gives confusing errors.
+//
+// This will create a new locked file that is fully initialized, and then
+// atomically replaces the original file using Linux's renameat2(2)
+// RENAME_EXCHANGE feature, which can atomically swap two paths.
+//
+//   1. First we take possession of the file's name (on an advisory basis using
+//      flock(2)) via the helper function `claim_event_ring_file`. That function
+//      opens the file with O_RDONLY, to avoid triggering anyone watching with
+//      `monad_event_ring_find_writer_pids` (the file will still appear to be
+//      a zombie). It places a LOCK_EX flock(2) to claim ownership of the file
+//      initialization process, so that the rest of the steps can deal with
+//      another daemon racing against us. Note that we do this _even though_
+//      we're only open with O_RDONLY, which Linux allows.
+//
+//   2. Next, we use the helper function `allocate_event_ring_file` to create
+//      the real file (called the "init" file) with the temporary file name
+//      `<file-name>.<our-pid>`; when this returns successfully, the file is
+//      advisory-locked and initialized
+//
+//   3. Finally, we atomically exchange the two filenames in the filesystem,
+//      then delete the "init" file's name (which now refers to the truncated
+//      "name-reservation" file)
+//
+// These functions use dir_fd relative functions like openat(2), linkat(2),
+// etc., because renameat2(2) is the only syscall that can use RENAME_EXCHANGE
+int create_owned_event_ring(
+    fs::path const &ring_file_path,
+    monad_event_ring_simple_config const *simple_cfg, int *ring_fd)
+{
+    std::string const file_name = ring_file_path.filename().string();
+    std::string const init_file_name =
+        std::format("{}.{}", file_name, getpid());
+
+    int dir_fd [[gnu::cleanup(cleanup_close)]] =
+        ring_file_path.has_parent_path()
+            ? open(ring_file_path.parent_path().c_str(), O_DIRECTORY | O_PATH)
+            : AT_FDCWD;
+    if (dir_fd == -1) {
+        int const rc = errno;
+        LOG_ERROR(
+            "open of event ring file parent directory {} failed",
+            ring_file_path.parent_path().c_str());
+        return rc;
+    }
+    if (int const rc = claim_event_ring_file(
+            dir_fd, file_name.c_str(), ring_file_path.c_str(), ring_fd)) {
+        return rc;
+    }
+
+    int init_ring_fd [[gnu::cleanup(cleanup_close)]] = -1;
+    if (int const rc = allocate_event_ring_file(
+            simple_cfg,
+            dir_fd,
+            init_file_name.c_str(),
+            ring_file_path.c_str(),
+            &init_ring_fd)) {
+        (void)unlinkat(dir_fd, file_name.c_str(), 0);
+        (void)unlinkat(dir_fd, init_file_name.c_str(), 0);
+        return rc;
+    }
+
+    if (renameat2(
+            dir_fd,
+            init_file_name.c_str(),
+            dir_fd,
+            file_name.c_str(),
+            RENAME_EXCHANGE) == -1) {
+        int const rc = errno;
+        (void)unlinkat(dir_fd, file_name.c_str(), 0);
+        (void)unlinkat(dir_fd, init_file_name.c_str(), 0);
+        LOG_ERROR(
+            "atomic exchange of {}/{} -> {}/{} failed: {} [{}]",
+            ring_file_path.parent_path().c_str(),
+            init_file_name,
+            ring_file_path.parent_path().c_str(),
+            file_name,
+            strerror(rc),
+            rc);
+        return rc;
+    }
+    (void)unlinkat(dir_fd, init_file_name.c_str(), 0);
+    std::swap(*ring_fd, init_ring_fd);
+    return 0;
+}
+
+// Call create_owned_event_ring, but with SIGTERM and SIGINT blocked while it
+// runs so we don't have any junk files lying around; those signals will be
+// unblocked again (if they were before) to receive any pending signals prior
+// to returning
+int create_owned_event_ring_nointr(
+    fs::path const &ring_file_path,
+    monad_event_ring_simple_config const *simple_cfg, int *ring_fd)
+{
+    sigset_t to_block;
+    sigset_t old_mask;
+
+    sigemptyset(&to_block);
+    sigaddset(&to_block, SIGINT);
+    sigaddset(&to_block, SIGTERM);
+    sigprocmask(SIG_BLOCK, &to_block, &old_mask);
+    int const rc = create_owned_event_ring(ring_file_path, simple_cfg, ring_fd);
+    sigprocmask(SIG_SETMASK, &old_mask, nullptr);
+    return rc;
+}
+
 MONAD_ANONYMOUS_NAMESPACE_END
 
 MONAD_NAMESPACE_BEGIN
@@ -121,8 +338,6 @@ try_parse_event_ring_config(std::string_view s)
 
 int init_execution_event_recorder(EventRingConfig ring_config)
 {
-    // Create with rw-rw-r--
-    constexpr mode_t mode = S_IRUSR | S_IWUSR | S_IRGRP | S_IWGRP | S_IROTH;
     MONAD_ASSERT(!g_exec_event_recorder, "recorder initialized twice?");
 
     if (!ring_config.event_ring_spec.contains('/')) {
@@ -142,94 +357,34 @@ int init_execution_event_recorder(EventRingConfig ring_config)
                                       '/' + ring_config.event_ring_spec;
     }
 
-    // Open the file and acquire a BSD-style exclusive lock on it; note there
-    // is no O_TRUNC here because it might already exist and we might not own
-    // it (e.g., if we're racing against another execution daemon started
-    // accidentally). In that case we'll either win or lose the race to acquire
-    // the lock, and will resize it only if we end up winning
-    char const *const ring_path = ring_config.event_ring_spec.c_str();
-    int ring_fd [[gnu::cleanup(cleanup_close)]] =
-        open(ring_path, O_RDWR | O_CREAT, mode);
-    if (ring_fd == -1) {
-        int const rc = errno;
+    // Check if the underlying filesystem supports MAP_HUGETLB
+    bool fs_supports_hugetlb;
+    if (int const rc = monad_check_path_supports_map_hugetlb(
+            ring_config.event_ring_spec.c_str(), &fs_supports_hugetlb)) {
         LOG_ERROR(
-            "open failed for event ring file `{}`: {} [{}]",
-            ring_path,
-            strerror(rc),
-            rc);
+            "event library error -- {}", monad_event_ring_get_last_error());
         return rc;
     }
-    if (flock(ring_fd, LOCK_EX | LOCK_NB) == -1) {
-        int const saved_errno = errno;
-        if (saved_errno == EWOULDBLOCK) {
-            pid_t owner_pid = 0;
-            size_t owner_pid_size = 1;
-
-            // Another process has the exclusive lock; find out who it is
-            (void)monad_event_ring_find_writer_pids(
-                ring_fd, &owner_pid, &owner_pid_size);
-            if (owner_pid == 0) {
-                LOG_ERROR(
-                    "event ring file `{}` is owned by an unknown other process",
-                    ring_path);
-            }
-            else {
-                LOG_ERROR(
-                    "event ring file `{}` is owned by pid {}",
-                    ring_path,
-                    owner_pid);
-            }
-            return saved_errno;
-        }
-        LOG_ERROR(
-            "flock on event ring file `{}` failed: {} ({})",
-            ring_path,
-            strerror(saved_errno),
-            saved_errno);
-        return saved_errno;
-    }
-
-    // monad_event_ring_init_simple uses fallocate(2), which is more general
-    // but won't shrink the file; that's not appropriate here since we're the
-    // exclusive owner; truncate it to zero first
-    if (ftruncate(ring_fd, 0) == -1) {
-        int const saved_errno = errno;
-        LOG_ERROR(
-            "ftruncate to zero failed for event ring file `{}` ({})",
-            ring_path,
-            strerror(saved_errno),
-            saved_errno);
-        return saved_errno;
+    if (!fs_supports_hugetlb) {
+        LOG_WARNING(
+            "file system hosting event ring file `{}` does not support "
+            "MAP_HUGETLB!",
+            ring_config.event_ring_spec);
     }
 
-    // We're the exclusive owner; initialize the event ring file
     monad_event_ring_simple_config const simple_cfg = {
         .descriptors_shift = ring_config.descriptors_shift,
         .payload_buf_shift = ring_config.payload_buf_shift,
         .context_large_pages = 0,
         .content_type = MONAD_EVENT_CONTENT_TYPE_EXEC,
         .schema_hash = g_monad_exec_event_schema_hash};
-    if (int const rc =
-            monad_event_ring_init_simple(&simple_cfg, ring_fd, 0, ring_path)) {
-        LOG_ERROR(
-            "event library error -- {}", monad_event_ring_get_last_error());
-        return rc;
-    }
 
-    // Check if the underlying filesystem supports MAP_HUGETLB
-    bool fs_supports_hugetlb;
-    if (int const rc = monad_check_path_supports_map_hugetlb(
-            ring_path, &fs_supports_hugetlb)) {
-        LOG_ERROR(
-            "event library error -- {}", monad_event_ring_get_last_error());
+    int ring_fd [[gnu::cleanup(cleanup_close)]] = -1;
+    if (int const rc = create_owned_event_ring_nointr(
+            ring_config.event_ring_spec, &simple_cfg, &ring_fd)) {
         return rc;
     }
-    if (!fs_supports_hugetlb) {
-        LOG_WARNING(
-            "file system hosting event ring file `{}` does not support "
-            "MAP_HUGETLB!",
-            ring_path);
-    }
+
     int const mmap_extra_flags =
         fs_supports_hugetlb ? MAP_POPULATE | MAP_HUGETLB : MAP_POPULATE;
 
@@ -241,16 +396,18 @@ int init_execution_event_recorder(EventRingConfig ring_config)
             mmap_extra_flags,
             ring_fd,
             0,
-            ring_path)) {
+            ring_config.event_ring_spec.c_str())) {
         LOG_ERROR(
             "event library error -- {}", monad_event_ring_get_last_error());
         return rc;
     }
 
     // Create the execution recorder object
-    g_exec_event_recorder =
-        std::make_unique<ExecutionEventRecorder>(ring_fd, ring_path, exec_ring);
-    LOG_INFO("execution event ring created: {}", ring_path);
+    g_exec_event_recorder = std::make_unique<ExecutionEventRecorder>(
+        ring_fd, ring_config.event_ring_spec.c_str(), exec_ring);
+    LOG_INFO(
+        "execution event ring created: {}",
+        ring_config.event_ring_spec.c_str());
     return 0;
 }
 
```
