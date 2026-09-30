# [?] [CVE-2019-18936] Pull UniValue subtree from Bitcoin Core

## Summary
Severity: Unknown
Chain: Bitcoin Cash
Component: bitcoin-cash-node/bitcoin-cash-node
Published: 2020-03-11
Source: https://github.com/bitcoin-cash-node/bitcoin-cash-node/commit/83252d07d20421beec388f7d29f36fc8371ee7d6
Type: security-commit

## Details
[CVE-2019-18936] Pull UniValue subtree from Bitcoin Core

Merge commit 'fd599a74e7d9e5700316c30d7c3ae44b86e343b7'

## Patch
### src/univalue/Makefile.am
```diff
@@ -95,6 +95,7 @@ TEST_FILES = \
 	$(TEST_DATA_DIR)/fail41.json \
 	$(TEST_DATA_DIR)/fail42.json \
 	$(TEST_DATA_DIR)/fail44.json \
+	$(TEST_DATA_DIR)/fail45.json \
 	$(TEST_DATA_DIR)/fail3.json \
 	$(TEST_DATA_DIR)/fail4.json \
 	$(TEST_DATA_DIR)/fail5.json \
@@ -105,6 +106,7 @@ TEST_FILES = \
 	$(TEST_DATA_DIR)/pass1.json \
 	$(TEST_DATA_DIR)/pass2.json \
 	$(TEST_DATA_DIR)/pass3.json \
+	$(TEST_DATA_DIR)/pass4.json \
 	$(TEST_DATA_DIR)/round1.json \
 	$(TEST_DATA_DIR)/round2.json \
 	$(TEST_DATA_DIR)/round3.json \
```

### src/univalue/README.md
```diff
@@ -30,3 +30,10 @@ $ make
 UniValue provides a single dynamic RAII C++ object class,
 and minimizes template use (contra json_spirit).
 
+## Library usage
+
+This is a fork of univalue used by Bitcoin Core. It is not maintained for usage
+by other projects. Notably, the API may break in non-backward-compatible ways.
+
+Other projects looking for a maintained library should use the upstream
+univalue at https://github.com/jgarzik/univalue.
```

### src/univalue/include/univalue.h
```diff
@@ -47,7 +47,6 @@ class UniValue {
         std::string s(val_);
         setStr(s);
     }
-    ~UniValue() {}
 
     void clear();
 
```

### src/univalue/lib/univalue_get.cpp
```diff
@@ -35,7 +35,7 @@ bool ParseInt32(const std::string& str, int32_t *out)
     errno = 0; // strtol will not set errno if valid
     long int n = strtol(str.c_str(), &endp, 10);
     if(out) *out = (int32_t)n;
-    // Note that strtol returns a *long int*, so even if strtol doesn't report a over/underflow
+    // Note that strtol returns a *long int*, so even if strtol doesn't report an over/underflow
     // we still have to check that the returned value is within the range of an *int32_t*. On 64-bit
     // platforms the size of these types may be different.
     return endp && *endp == 0 && !errno &&
```

### src/univalue/lib/univalue_read.cpp
```diff
@@ -8,6 +8,14 @@
 #include "univalue.h"
 #include "univalue_utffilter.h"
 
+/*
+ * According to stackexchange, the original json test suite wanted
+ * to limit depth to 22.  Widely-deployed PHP bails at depth 512,
+ * so we will follow PHP's lead, which should be more than sufficient
+ * (further stackexchange comments indicate depth > 32 rarely occurs).
+ */
+static const size_t MAX_JSON_DEPTH = 512;
+
 static bool json_isdigit(int ch)
 {
     return ((ch >= '0') && (ch <= '9'));
@@ -323,6 +331,9 @@ bool UniValue::read(const char *raw, size_t size)
                 stack.push_back(newTop);
             }
 
+            if (stack.size() > MAX_JSON_DEPTH)
+                return false;
+
             if (utyp == VOBJ)
                 setExpect(OBJ_NAME);
             else
```

### src/univalue/test/fail45.json
```diff
@@ -0,0 +1 @@
+[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]
```

### src/univalue/test/object.cpp
```diff
@@ -19,9 +19,10 @@
 #define BOOST_CHECK_THROW(stmt, excMatch) { \
         try { \
             (stmt); \
+            assert(0 && "No exception caught"); \
         } catch (excMatch & e) { \
 	} catch (...) { \
-	    assert(0); \
+	    assert(0 && "Wrong exception caught"); \
 	} \
     }
 #define BOOST_CHECK_NO_THROW(stmt) { \
```

### src/univalue/test/pass4.json
```diff
@@ -0,0 +1 @@
+[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]
```

### src/univalue/test/unitester.cpp
```diff
@@ -114,6 +114,7 @@ static const char *filenames[] = {
         "fail41.json",               // invalid unicode: unfinished UTF-8
         "fail42.json",               // valid json with garbage following a nul byte
         "fail44.json",               // unterminated string
+        "fail45.json",               // nested beyond max depth
         "fail3.json",
         "fail4.json",                // extra comma
         "fail5.json",
@@ -124,6 +125,7 @@ static const char *filenames[] = {
         "pass1.json",
         "pass2.json",
         "pass3.json",
+        "pass4.json",
         "round1.json",              // round-trip test
         "round2.json",              // unicode
         "round3.json",              // bare string
```
