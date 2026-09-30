# [?] fix(bb): suppress false-positive GCC -Wstringop-overflow in field_t::set_origin_tag

## Summary
Severity: Unknown
Chain: Aztec
Component: AztecProtocol/aztec-packages
Published: 2026-06-11
Source: https://github.com/AztecProtocol/aztec-packages/commit/6e8d2eede38824b31c2d1b4b59c81985fc8ba8b7
Type: security-commit

## Details
fix(bb): suppress false-positive GCC -Wstringop-overflow in field_t::set_origin_tag

## Patch
### barretenberg/cpp/src/barretenberg/stdlib/primitives/field/field.hpp
```diff
@@ -355,7 +355,20 @@ template <typename Builder_> class field_t {
         return result;
     }
 
-    void set_origin_tag(const OriginTag& new_tag) const { tag = new_tag; }
+    void set_origin_tag(const OriginTag& new_tag) const
+    {
+        // GCC -O3 mis-analyzes this defaulted OriginTag copy as a write into a zero-sized region when
+        // set_origin_tag is inlined through bigfield::self_reduce (-Werror=stringop-overflow). The destination
+        // is a fixed-size member; the warning is a known GCC false positive, so suppress it at the write.
+#if defined(__GNUC__) && !defined(__clang__)
+#pragma GCC diagnostic push
+#pragma GCC diagnostic ignored "-Wstringop-overflow"
+#endif
+        tag = new_tag;
+#if defined(__GNUC__) && !defined(__clang__)
+#pragma GCC diagnostic pop
+#endif
+    }
     OriginTag get_origin_tag() const { return tag; };
 
     /**
```
