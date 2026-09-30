# [?] GH-1062 Also guard against underflow

## Summary
Severity: Unknown
Chain: EOS/Vaulta
Component: AntelopeIO/leap
Published: 2023-05-10
Source: https://github.com/AntelopeIO/leap/commit/724be07d50eebca8b32ce088e37c819c56d01560
Type: security-commit

## Details
GH-1062 Also guard against underflow

## Patch
### libraries/libfc/include/fc/time.hpp
```diff
@@ -1,6 +1,7 @@
 #pragma once
 #include <cstdint>
 #include <string>
+#include <limits>
 
 #ifdef _MSC_VER
   #pragma warning (push)
@@ -49,12 +50,14 @@ namespace fc {
         std::string to_iso_string()const;
         static time_point from_iso_string( const std::string& s );
 
-        // protect against overflow
+        // protect against overflow/underflow
         constexpr time_point& safe_add( const microseconds& m ) {
            if (m.count() > 0 && elapsed > fc::microseconds::maximum() - m) {
               elapsed = microseconds::maximum();
-           } else { // does not guard against underflow
-              elapsed += m;
+           } else if (m.count() < 0 && elapsed.count() < std::numeric_limits<int64_t >::min() - m.count()) {
+              elapsed = microseconds(std::numeric_limits<int64_t >::min());
+           } else {
+             elapsed += m;
            }
            return *this;
         }
```
