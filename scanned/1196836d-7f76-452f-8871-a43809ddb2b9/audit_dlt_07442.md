# [?] wallet: Fix non-determinism in ParseHDKeypath(...). Avoid using an uninitialized variable in path calculation.

## Summary
Severity: Unknown
Chain: Bitcoin Cash
Component: bitcoin-cash-node/bitcoin-cash-node
Published: 2018-07-19
Source: https://github.com/bitcoin-cash-node/bitcoin-cash-node/commit/a3884c52a1ccba5b4483781799464d3b3242dfcc
Type: security-commit

## Details
wallet: Fix non-determinism in ParseHDKeypath(...). Avoid using an uninitialized variable in path calculation.

Summary:
 * wallet: Add error handling. Check return value of ParseUInt32(...) in ParseHDKeypath(...).

 * wallet: Add tests for ParseHDKeypath(...)

This is a backport of Core PR13712

Test Plan:
  make check

Reviewers: #bitcoin_abc, jasonbcox

Reviewed By: #bitcoin_abc, jasonbcox

Differential Revision: https://reviews.bitcoinabc.org/D4500

## Patch
### src/util/strencodings.cpp
```diff
@@ -832,7 +832,9 @@ bool ParseHDKeypath(const std::string &keypath_str,
             return false;
         }
         uint32_t number;
-        ParseUInt32(item, &number);
+        if (!ParseUInt32(item, &number)) {
+            return false;
+        }
         path |= number;
 
         keypath.push_back(path);
```

### src/wallet/test/psbt_wallet_tests.cpp
```diff
@@ -124,4 +124,93 @@ BOOST_AUTO_TEST_CASE(psbt_updater_test) {
         "008000");
 }
 
+BOOST_AUTO_TEST_CASE(parse_hd_keypath) {
+    std::vector<uint32_t> keypath;
+
+    BOOST_CHECK(ParseHDKeypath(
+        "1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1", keypath));
+    BOOST_CHECK(!ParseHDKeypath("///////////////////////////", keypath));
+
+    BOOST_CHECK(ParseHDKeypath(
+        "1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1'/1", keypath));
+    BOOST_CHECK(!ParseHDKeypath("//////////////////////////'/", keypath));
+
+    BOOST_CHECK(ParseHDKeypath(
+        "1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/", keypath));
+    BOOST_CHECK(!ParseHDKeypath("1///////////////////////////", keypath));
+
+    BOOST_CHECK(ParseHDKeypath(
+        "1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1'/", keypath));
+    BOOST_CHECK(!ParseHDKeypath("1/'//////////////////////////", keypath));
+
+    BOOST_CHECK(ParseHDKeypath("", keypath));
+    BOOST_CHECK(!ParseHDKeypath(" ", keypath));
+
+    BOOST_CHECK(ParseHDKeypath("0", keypath));
+    BOOST_CHECK(!ParseHDKeypath("O", keypath));
+
+    BOOST_CHECK(ParseHDKeypath("0000'/0000'/0000'", keypath));
+    BOOST_CHECK(!ParseHDKeypath("0000,/0000,/0000,", keypath));
+
+    BOOST_CHECK(ParseHDKeypath("01234", keypath));
+    BOOST_CHECK(!ParseHDKeypath("0x1234", keypath));
+
+    BOOST_CHECK(ParseHDKeypath("1", keypath));
+    BOOST_CHECK(!ParseHDKeypath(" 1", keypath));
+
+    BOOST_CHECK(ParseHDKeypath("42", keypath));
+    BOOST_CHECK(!ParseHDKeypath("m42", keypath));
+
+    // 4294967295 == 0xFFFFFFFF (uint32_t max)
+    BOOST_CHECK(ParseHDKeypath("4294967295", keypath));
+    // 4294967296 == 0xFFFFFFFF (uint32_t max) + 1
+    BOOST_CHECK(!ParseHDKeypath("4294967296", keypath));
+
+    BOOST_CHECK(ParseHDKeypath("m", keypath));
+    BOOST_CHECK(!ParseHDKeypath("n", keypath));
+
+    BOOST_CHECK(ParseHDKeypath("m/", keypath));
+    BOOST_CHECK(!ParseHDKeypath("n/", keypath));
+
+    BOOST_CHECK(ParseHDKeypath("m/0", keypath));
+    BOOST_CHECK(!ParseHDKeypath("n/0", keypath));
+
+    BOOST_CHECK(ParseHDKeypath("m/0'", keypath));
+    BOOST_CHECK(!ParseHDKeypath("m/0''", keypath));
+
+    BOOST_CHECK(ParseHDKeypath("m/0'/0'", keypath));
+    BOOST_CHECK(!ParseHDKeypath("m/'0/0'", keypath));
+
+    BOOST_CHECK(ParseHDKeypath("m/0/0", keypath));
+    BOOST_CHECK(!ParseHDKeypath("n/0/0", keypath));
+
+    BOOST_CHECK(ParseHDKeypath("m/0/0/00", keypath));
+    BOOST_CHECK(!ParseHDKeypath("m/0/0/f00", keypath));
+
+    BOOST_CHECK(ParseHDKeypath("m/0/0/"
+                               "00000000000000000000000000000000000000000000000"
+                               "0000000000000000000000000000000000000",
+                               keypath));
+    BOOST_CHECK(!ParseHDKeypath("m/1/1/"
+                                "1111111111111111111111111111111111111111111111"
+                                "11111111111111111111111111111111111111",
+                                keypath));
+
+    BOOST_CHECK(ParseHDKeypath("m/0/00/0", keypath));
+    BOOST_CHECK(!ParseHDKeypath("m/0'/00/'0", keypath));
+
+    BOOST_CHECK(ParseHDKeypath("m/1/", keypath));
+    BOOST_CHECK(!ParseHDKeypath("m/1//", keypath));
+
+    // 4294967295 == 0xFFFFFFFF (uint32_t max)
+    BOOST_CHECK(ParseHDKeypath("m/0/4294967295", keypath));
+    // 4294967296 == 0xFFFFFFFF (uint32_t max) + 1
+    BOOST_CHECK(!ParseHDKeypath("m/0/4294967296", keypath));
+
+    // 4294967295 == 0xFFFFFFFF (uint32_t max)
+    BOOST_CHECK(ParseHDKeypath("m/4294967295", keypath));
+    // 4294967296 == 0xFFFFFFFF (uint32_t max) + 1
+    BOOST_CHECK(!ParseHDKeypath("m/4294967296", keypath));
+}
+
 BOOST_AUTO_TEST_SUITE_END()
```
