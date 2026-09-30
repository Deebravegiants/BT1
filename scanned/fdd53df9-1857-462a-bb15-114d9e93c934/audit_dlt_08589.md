# [?] Detect CVE-2021-3520 when decompressing using LZ4

## Summary
Severity: Unknown
Chain: XRP
Component: XRPLF/rippled
Published: 2021-12-20
Source: https://github.com/XRPLF/rippled/commit/416ce35d7340572531f9658ed1917d1bfc29c524
Type: security-commit

## Details
Detect CVE-2021-3520 when decompressing using LZ4

## Patch
### src/ripple/basics/CompressionAlgorithms.h
```diff
@@ -65,26 +65,33 @@ lz4Compress(void const* in, std::size_t inSize, BufferFactory&& bf)
 
 /**
  * @param in Compressed data
- * @param inSize Size of compressed data
+ * @param inSizeUnchecked Size of compressed data
  * @param decompressed Buffer to hold decompressed data
- * @param decompressedSize Size of the decompressed buffer
+ * @param decompressedSizeUnchecked Size of the decompressed buffer
  * @return size of the decompressed data
  */
 inline std::size_t
 lz4Decompress(
     std::uint8_t const* in,
-    std::size_t inSize,
+    std::size_t inSizeUnchecked,
     std::uint8_t* decompressed,
-    std::size_t decompressedSize)
+    std::size_t decompressedSizeUnchecked)
 {
-    auto ret = LZ4_decompress_safe(
-        reinterpret_cast<const char*>(in),
-        reinterpret_cast<char*>(decompressed),
-        inSize,
-        decompressedSize);
+    int const inSize = static_cast<int>(inSizeUnchecked);
+    int const decompressedSize = static_cast<int>(decompressedSizeUnchecked);
+
+    if (inSize <= 0)
+        Throw<std::runtime_error>("lz4Decompress: integer overflow (input)");
+
+    if (decompressedSize <= 0)
+        Throw<std::runtime_error>("lz4Decompress: integer overflow (output)");
 
-    if (ret <= 0 || ret != decompressedSize)
-        Throw<std::runtime_error>("lz4 decompress: failed");
+    if (LZ4_decompress_safe(
+            reinterpret_cast<const char*>(in),
+            reinterpret_cast<char*>(decompressed),
+            inSize,
+            decompressedSize) != decompressedSize)
+        Throw<std::runtime_error>("lz4Decompress: failed");
 
     return decompressedSize;
 }
```

### src/ripple/nodestore/impl/codec.h
```diff
@@ -42,22 +42,30 @@ template <class BufferFactory>
 std::pair<void const*, std::size_t>
 lz4_decompress(void const* in, std::size_t in_size, BufferFactory&& bf)
 {
-    using std::runtime_error;
-    using namespace nudb::detail;
-    std::pair<void const*, std::size_t> result;
-    std::uint8_t const* p = reinterpret_cast<std::uint8_t const*>(in);
-    auto const n = read_varint(p, in_size, result.second);
-    if (n == 0)
-        Throw<std::runtime_error>("lz4 decompress: n == 0");
-    void* const out = bf(result.second);
-    result.first = out;
+    if (static_cast<int>(in_size) < 0)
+        Throw<std::runtime_error>("lz4_decompress: integer overflow (input)");
+
+    std::size_t outSize = 0;
+
+    auto const n = read_varint(
+        reinterpret_cast<std::uint8_t const*>(in), in_size, outSize);
+
+    if (n == 0 || n >= in_size)
+        Throw<std::runtime_error>("lz4_decompress: invalid blob");
+
+    if (static_cast<int>(outSize) <= 0)
+        Throw<std::runtime_error>("lz4_decompress: integer overflow (output)");
+
+    void* const out = bf(outSize);
+
     if (LZ4_decompress_safe(
             reinterpret_cast<char const*>(in) + n,
             reinterpret_cast<char*>(out),
-            in_size - n,
-            result.second) != result.second)
-        Throw<std::runtime_error>("lz4 decompress: LZ4_decompress_safe");
-    return result;
+            static_cast<int>(in_size - n),
+            static_cast<int>(outSize)) != static_cast<int>(outSize))
+        Throw<std::runtime_error>("lz4_decompress: LZ4_decompress_safe");
+
+    return {out, outSize};
 }
 
 template <class BufferFactory>
```
