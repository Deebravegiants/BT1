# [?] [mpt] Fix legacy DB upgrade crash from num_cnv_chunks=0 underflow

## Summary
Severity: Unknown
Chain: Monad
Component: monad-crypto/monad
Published: 2026-06-17
Source: https://github.com/category-labs/monad/commit/fdb541ae8135acddaf5a26f7d1222937eeb75a24
Type: security-commit

## Details
[mpt] Fix legacy DB upgrade crash from num_cnv_chunks=0 underflow

DBs created before the num_cnv_chunks footer field existed store 0 there.
storage_pool::device_t::cnv_chunks() returned that raw 0, so
DbMetadataContext::ring_max_chunks_() computed (uint32_t)0 - 1 = 0xFFFFFFFF
and map_ring_storage_ tried to reserve ~exabytes of VA, aborting
monad-mpt --upgrade with an opaque "Assertion 'r != MAP_FAILED'".

Normalize the legacy 0 to the historical default of 3 in cnv_chunks()
itself -- the single source of truth its two callers want; the inline 0->3
fallbacks in fill_chunks_ and the flag-mismatch warning now defer to it.

Add two operator-facing aborts so a genuinely under-provisioned or corrupt
pool fails with an actionable message instead of the opaque mmap assertion:
ring_max_chunks_() rejects pools with fewer than 2 conventional chunks, and
map_ring_storage_ rejects a ring whose recorded length exceeds pool capacity.

Regression test: a footer of 0 (byte-identical to a legacy DB) must open on
both create and reopen; it aborted before this fix.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

## Patch
### category/async/storage_pool.cpp
```diff
@@ -54,6 +54,10 @@
 
 MONAD_ASYNC_NAMESPACE_BEGIN
 
+// DBs created before the num_cnv_chunks footer field existed store 0 there;
+// such pools were always carved with this many conventional chunks.
+static constexpr uint32_t legacy_default_num_cnv_chunks = 3;
+
 std::filesystem::path storage_pool::device_t::current_path() const
 {
     std::filesystem::path::string_type ret;
@@ -84,7 +88,8 @@ size_t storage_pool::device_t::chunks() const
 size_t storage_pool::device_t::cnv_chunks() const
 {
     MONAD_ASSERT(!is_zoned_device(), "zonefs support isn't implemented yet");
-    return metadata_->num_cnv_chunks;
+    return metadata_->num_cnv_chunks == 0 ? legacy_default_num_cnv_chunks
+                                          : metadata_->num_cnv_chunks;
 }
 
 std::pair<file_offset_t, file_offset_t> storage_pool::device_t::capacity() const
@@ -474,16 +479,18 @@ storage_pool::device_t storage_pool::make_device_(
         }
         total_size =
             metadata_footer->total_size(static_cast<size_t>(stat.st_size));
-        if (flags.num_cnv_chunks > metadata_footer->num_cnv_chunks) {
+        uint32_t const stored_num_cnv_chunks =
+            metadata_footer->num_cnv_chunks == 0
+                ? legacy_default_num_cnv_chunks
+                : metadata_footer->num_cnv_chunks;
+        if (flags.num_cnv_chunks > stored_num_cnv_chunks) {
             LOG_WARNING(
                 "Flag-specified num_cnv_chunks ({}) is greater than the value "
                 "stored in metadata ({}). This setting will be ignored. "
                 "Existing databases cannot be reconfigured to use more chunks, "
                 "create a new database if you need a higher num_cnv_chunks.",
                 flags.num_cnv_chunks,
-                metadata_footer->num_cnv_chunks == 0
-                    ? 3
-                    : metadata_footer->num_cnv_chunks);
+                stored_num_cnv_chunks);
         }
     }
     size_t const offset = round_down_align<CPU_PAGE_BITS>(
@@ -524,13 +531,8 @@ void storage_pool::fill_chunks_(creation_flags const &flags)
         fnv1a_hash<uint32_t>::add(
             hashshouldbe, uint32_t(device.unique_hash_ >> 32));
     }
-    // Backward compatibility: databases created before `num_cnv_chunks` was
-    // added have this field set to 0. Treat 0 as the legacy default of 3
-    // chunks.
     uint32_t const cnv_chunks_count =
-        devices_[0].metadata_->num_cnv_chunks == 0
-            ? 3
-            : devices_[0].metadata_->num_cnv_chunks;
+        static_cast<uint32_t>(devices_[0].cnv_chunks());
     std::vector<size_t> chunks;
     size_t total = 0;
     chunks.reserve(devices_.size());
```

### category/mpt/db_metadata_context.cpp
```diff
@@ -433,7 +433,9 @@ DbMetadataContext::DbMetadataContext(AsyncIO &io)
 void DbMetadataContext::map_ring_a_storage()
 {
     map_ring_storage_(
-        copies_[0].main->root_offsets.storage_, &metadata_copy::ring_a_span);
+        copies_[0].main->root_offsets.storage_,
+        &metadata_copy::ring_a_span,
+        "ring_a");
     LOG_INFO(
         "Database ring_a is configured with {} chunks (of {} max)",
         copies_[0].main->root_offsets.storage_.cnv_chunks_len,
@@ -444,7 +446,8 @@ void DbMetadataContext::map_ring_b_storage()
 {
     map_ring_storage_(
         copies_[0].main->secondary_timeline.storage_,
-        &metadata_copy::ring_b_span);
+        &metadata_copy::ring_b_span,
+        "ring_b");
     LOG_INFO(
         "Database ring_b is configured with {} chunks (of {} max)",
         copies_[0].main->secondary_timeline.storage_.cnv_chunks_len,
@@ -453,8 +456,16 @@ void DbMetadataContext::map_ring_b_storage()
 
 uint32_t DbMetadataContext::ring_max_chunks_() const noexcept
 {
-    return static_cast<uint32_t>(
-               io_->storage_pool().devices()[0].cnv_chunks()) -
+    auto const cnv_chunks = io_->storage_pool().devices()[0].cnv_chunks();
+    if (cnv_chunks < 2) {
+        MONAD_ABORT_PRINTF(
+            "storage pool has %zu conventional chunk(s); at least 2 are "
+            "required (1 for db_metadata + at least 1 for the root offsets "
+            "ring). The pool metadata is corrupt or the pool was created with "
+            "too few conventional chunks.",
+            cnv_chunks);
+    }
+    return static_cast<uint32_t>(cnv_chunks) -
            1 /* chunk 0 holds db_metadata */;
 }
 
```

### category/mpt/db_metadata_context.hpp
```diff
@@ -396,9 +396,18 @@ class DbMetadataContext
     template <typename Storage>
     void map_ring_storage_(
         Storage const &storage,
-        std::span<chunk_offset_t> metadata_copy::*span_field)
+        std::span<chunk_offset_t> metadata_copy::*span_field,
+        char const *const ring_name)
     {
         auto const max_chunks = ring_max_chunks_();
+        MONAD_ASSERT_PRINTF(
+            storage.cnv_chunks_len <= max_chunks,
+            "%s requires %u conventional chunk(s) but the storage pool "
+            "provides only %u for ring data; the pool was created with fewer "
+            "conventional chunks than this DB needs",
+            ring_name,
+            storage.cnv_chunks_len,
+            max_chunks);
         auto const map_bytes = map_bytes_per_chunk_();
         auto const reservation_bytes = max_chunks * map_bytes;
         auto const entries_per_chunk = map_bytes / sizeof(chunk_offset_t);
```

### category/mpt/test/update_aux_test.cpp
```diff
@@ -271,6 +271,65 @@ TEST(update_aux_test, configurable_root_offset_chunks)
     remove(filename);
 }
 
+// A DB created before the num_cnv_chunks footer field existed stores 0 there.
+// The pool must treat that as the legacy default of 3 conventional chunks
+// (1 for metadata + 2 for ring_a), not as a raw 0 that underflows
+// ring_max_chunks_() to UINT32_MAX and aborts the mmap on reopen/upgrade.
+// A footer of 0 is exactly what `flags.num_cnv_chunks = 0` writes, so it
+// reproduces the legacy layout without an on-disk fixture.
+TEST(update_aux_test, legacy_zero_num_cnv_chunks_footer)
+{
+    auto path_template = (MONAD_ASYNC_NAMESPACE::working_temporary_directory() /
+                          "monad_update_aux_test_XXXXXX")
+                             .native();
+    int const fd = ::mkstemp(path_template.data());
+    MONAD_ASSERT(fd != -1);
+    MONAD_ASSERT(-1 != ::ftruncate(fd, 8UL << 30)); // 8GB
+    ::close(fd);
+    std::filesystem::path const filename{path_template};
+
+    monad::io::Ring ring1;
+    monad::io::Ring ring2;
+    monad::io::Buffers testbuf =
+        monad::io::make_buffers_for_segregated_read_write(
+            ring1,
+            ring2,
+            2,
+            4,
+            monad::async::AsyncIO::MONAD_IO_BUFFERS_READ_SIZE,
+            monad::async::AsyncIO::MONAD_IO_BUFFERS_WRITE_SIZE);
+    monad::async::storage_pool::creation_flags flags;
+    flags.num_cnv_chunks = 0; // legacy footer
+    {
+        monad::async::storage_pool pool(
+            std::span{&filename, 1},
+            monad::async::storage_pool::mode::truncate,
+            flags);
+        EXPECT_EQ(pool.chunks(monad::async::storage_pool::cnv), 3);
+
+        monad::async::AsyncIO testio(pool, testbuf);
+        monad::mpt::UpdateAux const aux(testio);
+
+        EXPECT_EQ(aux.metadata_ctx().main()->root_offsets.cnv_chunks_len(), 2);
+        EXPECT_EQ(
+            aux.metadata_ctx().main()->secondary_timeline.cnv_chunks_len(), 0);
+    }
+    {
+        // Reopen exercises map_ring_a_storage — the path that underflowed.
+        monad::async::storage_pool pool(
+            std::span{&filename, 1},
+            monad::async::storage_pool::mode::open_existing,
+            flags);
+        EXPECT_EQ(pool.chunks(monad::async::storage_pool::cnv), 3);
+        monad::async::AsyncIO testio(pool, testbuf);
+        monad::mpt::UpdateAux const aux(testio);
+        EXPECT_EQ(aux.metadata_ctx().main()->root_offsets.cnv_chunks_len(), 2);
+        EXPECT_EQ(
+            aux.metadata_ctx().main()->secondary_timeline.cnv_chunks_len(), 0);
+    }
+    remove(filename);
+}
+
 // -------------------------------------------------------------------
 // Secondary timeline ring and lifecycle tests (UpdateAux-level)
 // -------------------------------------------------------------------
```
