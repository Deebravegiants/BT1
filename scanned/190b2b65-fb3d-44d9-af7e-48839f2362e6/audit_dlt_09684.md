# [?] fix counter overflow problem

## Summary
Severity: Unknown
Chain: EOS/Vaulta
Component: AntelopeIO/leap
Published: 2022-12-20
Source: https://github.com/AntelopeIO/leap/commit/e0aa788ce25c9f5eaaa46a9c21df024f417dca49
Type: security-commit

## Details
fix counter overflow problem

## Patch
### libraries/state_history/include/eosio/state_history/log.hpp
```diff
@@ -16,7 +16,7 @@
 
 #include <boost/iostreams/device/file.hpp>
 #include <boost/iostreams/device/file_descriptor.hpp>
-#include <boost/iostreams/filter/counter.hpp>
+// #include <boost/iostreams/filter/counter.hpp>
 #include <boost/iostreams/filter/zlib.hpp>
 #include <boost/iostreams/filtering_streambuf.hpp>
 #include <boost/iostreams/restrict.hpp>
@@ -91,6 +91,43 @@ struct maybe_locked_compress_stream {
    }
 };
 
+// directly adapt from boost/iostreams/filter/counter.hpp and change the type of chars_ to uint64_t.
+class counter  {
+public:
+    typedef char char_type;
+    struct category
+        : bio::dual_use,
+          bio::filter_tag,
+          bio::multichar_tag,
+          bio::optimally_buffered_tag
+        { };
+    explicit counter(uint64_t first_char = 0)
+        : chars_(first_char)
+        { }
+    uint64_t characters() const { return chars_; }
+    std::streamsize optimal_buffer_size() const { return 0; }
+
+    template<typename Source>
+    std::streamsize read(Source& src, char_type* s, std::streamsize n)
+    {
+        std::streamsize result = bio::read(src, s, n);
+        if (result == -1)
+            return -1;
+        chars_ += result;
+        return result;
+    }
+
+    template<typename Sink>
+    std::streamsize write(Sink& snk, const char_type* s, std::streamsize n)
+    {
+        std::streamsize result = bio::write(snk, s, n);
+        chars_ += result;
+        return result;
+    }
+private:
+    uint64_t chars_;
+};
+
 
 class state_history_log {
  private:
@@ -312,8 +349,10 @@ class state_history_log {
       log.read((char*)&s, sizeof(s));
       if (s == 1 && payload_size > (s + sizeof(uint32_t))) {
          compressed_size = payload_size - sizeof(uint32_t) - sizeof(uint64_t);
-         uint64_t decompressed_size;
+         uint64_t decompressed_size = 0;
          log.read((char*)&decompressed_size, sizeof(decompressed_size));
+
+         EOS_ASSERT(decompressed_size < 0x8000000000000000, chain::plugin_exception, "error reading decompressed_size=${decompressed_size},  file = ${fn}, pos=${pos}", ("decompressed_size", decompressed_size)("fn", log.get_file_path().string())("pos", log.tellp()));
          result.emplace<maybe_locked_compress_stream>(this, log, compressed_size);
          return decompressed_size;
 
@@ -350,7 +389,7 @@ class state_history_log {
 
          namespace bio = boost::iostreams;
 
-         bio::counter cnt;
+         counter cnt;
          {
             bio::filtering_ostreambuf buf;
             buf.push(boost::ref(cnt));
```
