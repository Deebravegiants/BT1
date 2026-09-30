# [?] Fix node crash because mod zero

## Summary
Severity: Unknown
Chain: Zilliqa
Component: Zilliqa/zq1
Published: 2019-01-16
Source: https://github.com/Zilliqa/zq1/commit/dba0c37777c788a890c2254d06af8f52f9b2b96a
Type: security-commit

## Details
Fix node crash because mod zero

## Patch
### src/libNetwork/DataSender.cpp
```diff
@@ -284,7 +284,7 @@ bool DataSender::SendDataToOthers(
 
     uint16_t randomDigits =
         DataConversion::charArrTo16Bits(hashForRandom.asBytes());
-    bool committeeTooSmall = tmpCommittee.size() < TX_SHARING_CLUSTER_SIZE;
+    bool committeeTooSmall = tmpCommittee.size() <= TX_SHARING_CLUSTER_SIZE;
     uint16_t nodeToSendToLookUpLo =
         committeeTooSmall
             ? 0
```
