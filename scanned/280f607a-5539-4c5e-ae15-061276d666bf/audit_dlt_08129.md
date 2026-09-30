# [?] unit_tests: fix use after free in serialization test

## Summary
Severity: Unknown
Chain: Monero
Component: monero-project/monero
Published: 2021-09-08
Source: https://github.com/monero-project/monero/commit/5eaedb51b9e618a1c522674b7c14b90778e6f32d
Type: security-commit

## Details
unit_tests: fix use after free in serialization test

## Patch
### tests/unit_tests/serialization.cpp
```diff
@@ -132,7 +132,8 @@ TEST(Serialization, BinaryArchiveInts) {
   ASSERT_EQ(8, oss.str().size());
   ASSERT_EQ(string("\0\0\0\0\xff\0\0\0", 8), oss.str());
 
-  binary_archive<false> iar{epee::strspan<std::uint8_t>(oss.str())};
+  const std::string s = oss.str();
+  binary_archive<false> iar{epee::strspan<std::uint8_t>(s)};
   iar.serialize_int(x1);
   ASSERT_EQ(8, iar.getpos());
   ASSERT_TRUE(iar.good());
@@ -150,7 +151,8 @@ TEST(Serialization, BinaryArchiveVarInts) {
   ASSERT_EQ(6, oss.str().size());
   ASSERT_EQ(string("\x80\x80\x80\x80\xF0\x1F", 6), oss.str());
 
-  binary_archive<false> iar{epee::strspan<std::uint8_t>(oss.str())};
+  const std::string s = oss.str();
+  binary_archive<false> iar{epee::strspan<std::uint8_t>(s)};
   iar.serialize_varint(x1);
   ASSERT_TRUE(iar.good());
   ASSERT_EQ(x, x1);
```
