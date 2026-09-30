# [?] fix median overflow bug

## Summary
Severity: Unknown
Chain: Monero
Component: monero-project/monero
Published: 2021-08-13
Source: https://github.com/monero-project/monero/commit/426dbf434b54f4ef4c40b1887bb13194c2caacbf
Type: security-commit

## Details
fix median overflow bug

## Patch
### contrib/epee/include/stats.inl
```diff
@@ -1,6 +1,7 @@
 #include <math.h>
 #include <limits>
 #include <algorithm>
+#include "misc_language.h"
 #include "stats.h"
 
 enum
@@ -86,7 +87,7 @@ Tpod Stats<T, Tpod>::get_median() const
     }
     else
     {
-      median = (sorted[(sorted.size() - 1) / 2] + sorted[sorted.size() / 2]) / 2;
+      median = epee::misc_utils::get_mid(sorted[(sorted.size() - 1) / 2], sorted[sorted.size() / 2]);
     }
     set_cached(bit_median);
   }
```
