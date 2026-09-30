# [?] Fix potential buffer overflow when using HexStrToStdArray

## Summary
Severity: Unknown
Chain: Zilliqa
Component: Zilliqa/zq1
Published: 2018-12-05
Source: https://github.com/Zilliqa/zq1/commit/c3c3e12097fa3da45d18edc8b83722bbee7c3fc5
Type: security-commit

## Details
Fix potential buffer overflow when using HexStrToStdArray

## Patch
### src/libDirectoryService/PoWProcessing.cpp
```diff
@@ -152,6 +152,21 @@ bool DirectoryService::ProcessPoWSubmission(
     return false;
   }
 
+  if (resultingHash.size() != 64) {
+    LOG_EPOCH(WARNING, to_string(m_mediator.m_currentEpochNum).c_str(),
+              "Wrong resultingHash size "
+                  << resultingHash.size() << " submitted by "
+                  << submitterPeer.GetPrintableIPAddress());
+    return false;
+  }
+
+  if (mixHash.size() != 64) {
+    LOG_EPOCH(WARNING, to_string(m_mediator.m_currentEpochNum).c_str(),
+              "Wrong mixHash size " << mixHash.size() << " submitted by "
+                                    << submitterPeer.GetPrintableIPAddress());
+    return false;
+  }
+
   {
     std::unique_lock<std::mutex> lk(m_mutexPowSolution);
     m_powSolutions.emplace_back(DSPowSolution(
```

### src/libUtils/DataConversion.cpp
```diff
@@ -18,85 +18,58 @@
  */
 
 #include "DataConversion.h"
-#include <sstream>
 
-const std::vector<unsigned char> DataConversion::HexStrToUint8Vec(
-    const std::string& hex_input) {
-  std::string in(hex_input);
-  std::vector<uint8_t> out;
-  boost::algorithm::unhex(in.begin(), in.end(), std::back_inserter(out));
+using namespace std;
+
+const vector<unsigned char> DataConversion::HexStrToUint8Vec(
+    const string& hex_input) {
+  vector<uint8_t> out;
+  boost::algorithm::unhex(hex_input.begin(), hex_input.end(),
+                          back_inserter(out));
   return out;
 }
 
-const std::array<unsigned char, 32> DataConversion::HexStrToStdArray(
-    const std::string& hex_input) {
-  std::string in(hex_input);
-  std::array<unsigned char, 32> d;
-  std::vector<unsigned char> v = HexStrToUint8Vec(hex_input);
-  std::copy(std::begin(v), std::end(v),
-            std::begin(d));  // this is the recommended way
+const array<unsigned char, 32> DataConversion::HexStrToStdArray(
+    const string& hex_input) {
+  array<unsigned char, 32> d = {0};
+  vector<unsigned char> v = HexStrToUint8Vec(hex_input);
+  copy(v.begin(), v.begin() + min((int)v.size(), 32), d.begin());
   return d;
 }
 
-const std::array<unsigned char, 64> DataConversion::HexStrToStdArray64(
-    const std::string& hex_input) {
-  std::string in(hex_input);
-  std::array<unsigned char, 64> d;
-  std::vector<unsigned char> v = HexStrToUint8Vec(hex_input);
-  std::copy(std::begin(v), std::end(v),
-            std::begin(d));  // this is the recommended way
+const array<unsigned char, 64> DataConversion::HexStrToStdArray64(
+    const string& hex_input) {
+  array<unsigned char, 64> d = {0};
+  vector<unsigned char> v = HexStrToUint8Vec(hex_input);
+  copy(v.begin(), v.begin() + min((int)v.size(), 64), d.begin());
   return d;
 }
 
-const std::string DataConversion::Uint8VecToHexStr(
-    const std::vector<unsigned char>& hex_vec) {
-  std::string str;
-  boost::algorithm::hex(hex_vec.begin(), hex_vec.end(),
-                        std::back_inserter(str));
+const string DataConversion::Uint8VecToHexStr(
+    const vector<unsigned char>& hex_vec) {
+  string str;
+  boost::algorithm::hex(hex_vec.begin(), hex_vec.end(), back_inserter(str));
   return str;
 }
 
-const std::string DataConversion::Uint8VecToHexStr(
-    const std::vector<unsigned char>& hex_vec, unsigned int offset,
+const string DataConversion::Uint8VecToHexStr(
+    const vector<unsigned char>& hex_vec, unsigned int offset,
     unsigned int len) {
-  std::string str;
+  string str;
   boost::algorithm::hex(hex_vec.begin() + offset,
-                        hex_vec.begin() + offset + len,
-                        std::back_inserter(str));
+                        hex_vec.begin() + offset + len, back_inserter(str));
   return str;
 }
 
-std::string DataConversion::SerializableToHexStr(const Serializable& input) {
-  std::vector<unsigned char> tmp;
+string DataConversion::SerializableToHexStr(const Serializable& input) {
+  vector<unsigned char> tmp;
   input.Serialize(tmp, 0);
-  std::string str;
-  boost::algorithm::hex(tmp.begin(), tmp.end(), std::back_inserter(str));
+  string str;
+  boost::algorithm::hex(tmp.begin(), tmp.end(), back_inserter(str));
   return str;
 }
 
-const std::vector<unsigned char> DataConversion::StringToCharArray(
-    const std::string& input) {
-  std::vector<unsigned char> v;
-  v.resize(input.size());
-
-  std::copy(input.begin(), input.end(), v.begin());
-
-  return v;
-}
-
-const std::string DataConversion::CharArrayToString(
-    const std::vector<unsigned char>& v) {
-  std::string ret;
-
-  ret.resize(v.size());
-
-  copy(v.begin(), v.end(), ret.begin());
-
-  return ret;
-}
-
-uint16_t DataConversion::charArrTo16Bits(
-    const std::vector<unsigned char>& hex_arr) {
+uint16_t DataConversion::charArrTo16Bits(const vector<unsigned char>& hex_arr) {
   if (hex_arr.size() == 0) {
     return 0;
   }
```

### src/libUtils/DataConversion.h
```diff
@@ -64,11 +64,15 @@ class DataConversion {
   /// Converts a serializable object to alphanumeric hex string.
   static std::string SerializableToHexStr(const Serializable& input);
 
-  static const std::string CharArrayToString(
-      const std::vector<unsigned char>& v);
+  static inline const std::string CharArrayToString(
+      const std::vector<unsigned char>& v) {
+    return std::string(v.begin(), v.end());
+  }
 
-  static const std::vector<unsigned char> StringToCharArray(
-      const std::string& input);
+  static inline const std::vector<unsigned char> StringToCharArray(
+      const std::string& input) {
+    return std::vector<unsigned char>(input.begin(), input.end());
+  }
 
   static uint16_t charArrTo16Bits(const std::vector<unsigned char>& hex_arr);
 };
```
