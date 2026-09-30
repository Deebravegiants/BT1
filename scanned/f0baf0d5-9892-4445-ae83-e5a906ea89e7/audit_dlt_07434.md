# [?] Fix potential timedata overflow

## Summary
Severity: Unknown
Chain: Bitcoin Cash
Component: bitcoin-cash-node/bitcoin-cash-node
Published: 2020-05-11
Source: https://github.com/bitcoin-cash-node/bitcoin-cash-node/commit/062494875447ccc886b838c9c18c19841977561e
Type: security-commit

## Details
Fix potential timedata overflow

Summary:
The add before division can potentially cause an overflow.
If we divide before adding, no overflow can occur.

Test Plan: `ninja check`

Reviewers: #bitcoin_abc, Fabien, deadalnix

Reviewed By: #bitcoin_abc, Fabien, deadalnix

Subscribers: deadalnix, Fabien

Differential Revision: https://reviews.bitcoinabc.org/D6025

## Patch
### src/timedata.h
```diff
@@ -50,8 +50,9 @@ template <typename T> class CMedianFilter {
             return vSorted[vSortedSize / 2];
         } else {
             // Even number of elements
-            return (vSorted[vSortedSize / 2 - 1] + vSorted[vSortedSize / 2]) /
-                   2;
+            auto left = vSorted[vSortedSize / 2 - 1];
+            auto right = vSorted[vSortedSize / 2];
+            return left / 2 + right / 2 + (left & right & 1);
         }
     }
 
```
