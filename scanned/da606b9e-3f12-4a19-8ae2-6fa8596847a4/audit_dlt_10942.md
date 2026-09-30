# [?] fix deadlock

## Summary
Severity: Unknown
Chain: Zilliqa
Component: Zilliqa/zq1
Published: 2018-11-20
Source: https://github.com/Zilliqa/zq1/commit/ae7ff05154eed78aae32df03a43d28dd3a7f621f
Type: security-commit

## Details
fix deadlock

## Patch
### src/libData/AccountData/AccountStore.cpp
```diff
@@ -98,9 +98,10 @@ bool AccountStore::Deserialize(const vector<unsigned char>& src,
                                unsigned int offset) {
   LOG_MARKER();
 
-  unique_lock<shared_timed_mutex> g(m_mutexPrimary);
-
   this->Init();
+
+  unique_lock<shared_timed_mutex> g(m_mutexPrimary);
+  
   if (!Messenger::GetAccountStore(src, offset, *this)) {
     LOG_GENERAL(WARNING, "Messenger::GetAccountStore failed.");
     return false;
```
