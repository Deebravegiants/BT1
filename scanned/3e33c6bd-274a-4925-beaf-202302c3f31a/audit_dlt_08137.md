# [?] Fix overflow issue in epee:misc_utils::rolling_median_t and median(), with unit test

## Summary
Severity: Unknown
Chain: Monero
Component: monero-project/monero
Published: 2020-07-21
Source: https://github.com/monero-project/monero/commit/85efc88c1edc7371ca5c8722c896fd64a258ddd2
Type: security-commit

## Details
Fix overflow issue in epee:misc_utils::rolling_median_t and median(), with unit test

## Patch
### contrib/epee/include/misc_language.h
```diff
@@ -106,6 +106,14 @@ namespace misc_utils
 		return true;
 	}
 
+  template <typename T>
+  T get_mid(const T &a, const T &b)
+  {
+    //returns the average of two numbers; overflow safe and works with at least all integral and floating point types
+    //(a+b)/2 = (a/2) + (b/2) + ((a - 2*(a/2)) + (b - 2*(b/2)))/2
+    return (a/2) + (b/2) + ((a - 2*(a/2)) + (b - 2*(b/2)))/2;
+  }
+
   template<class type_vec_type>
   type_vec_type median(std::vector<type_vec_type> &v)
   {
@@ -122,7 +130,7 @@ namespace misc_utils
       return v[n];
     }else 
     {//2, 4, 6...
-      return (v[n-1] + v[n])/2;
+      return get_mid<type_vec_type>(v[n-1],v[n]);
     }
 
   }
```

### contrib/epee/include/rolling_median.h
```diff
@@ -34,6 +34,8 @@
 
 #pragma once
 
+#include "misc_language.h"
+
 #include <stdlib.h>
 #include <stdint.h>
 
@@ -226,7 +228,7 @@ struct rolling_median_t
     Item v = data[heap[0]];
     if (minCt < maxCt)
     {
-      v = (v + data[heap[-1]]) / 2;
+      v = get_mid<Item>(v, data[heap[-1]]);
     }
     return v;
   }
```

### tests/unit_tests/rolling_median.cpp
```diff
@@ -170,6 +170,17 @@ TEST(rolling_median, history_blind)
   }
 }
 
+TEST(rolling_median, overflow)
+{
+  epee::misc_utils::rolling_median_t<uint64_t> m(2);
+
+  uint64_t over_half = static_cast<uint64_t>(3) << static_cast<uint64_t>(62);
+  m.insert(over_half);
+  m.insert(over_half);
+  ASSERT_EQ((over_half + over_half) < over_half, true);
+  ASSERT_EQ(over_half, m.median());
+}
+
 TEST(rolling_median, size)
 {
   epee::misc_utils::rolling_median_t<uint64_t> m(10);
```
