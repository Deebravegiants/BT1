# [?] Merge bitcoin/bitcoin#36321: net: cast vector size to avoid overflow, truncation, sign change

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoin/bitcoin
Published: 2026-09-29
Source: https://github.com/bitcoin/bitcoin/commit/ced4c6e6ab472fe2a60ad5c379f76962b61b6f34
Type: security-commit

## Details
Merge bitcoin/bitcoin#36321: net: cast vector size to avoid overflow, truncation, sign change

308cd670195d908fbd50caf76a8a215386121bd0 net: cast vector size to avoid overflow, truncation, sign change (Eugene Siegel)

Pull request description:

  When running with `-fsanitize=integer` compiled, the following can error [here](https://github.com/bitcoin/bitcoin/blob/b3f846ec3e5c21b08779ac6c13475f3ab37e7d9c/src/net_processing.cpp#L3662):

  ```
  SUMMARY: UndefinedBehaviorSanitizer: unsigned-integer-overflow /bitcoin/src/net_processing.cpp:3662:33
  SUMMARY: UndefinedBehaviorSanitizer: implicit-signed-integer-truncation-or-sign-change /bitcoin/src/net_processing.cpp:3662:18
  ```

  When `stop_index->nHeight` is less than `CFCHECKPT_INTERVAL`, the `headers` vector will be empty. This will just set the loop counter to -1 and never enter the loop, so this is harmless anyways. Fix this by casting `headers.size()` to `int`.

ACKs for top commit:
  maflcko:
    lgtm ACK 308cd670195d908fbd50caf76a8a215386121bd0
  davidgumberg:
    crACK https://github.com/bitcoin/bitcoin/commit/308cd670195d908fbd50caf76a8a215386121bd0

Tree-SHA512: 1074667b644e42507b32043e98a0541fff6de9a3711003a43b9874b31956a8e10efe65af89ed2b23322a7aa3df7d6a8606db5c1ab342f070a625b9e9650ae1fa

## Patch
### src/net_processing.cpp
```diff
@@ -3659,7 +3659,7 @@ void PeerManagerImpl::ProcessGetCFCheckPt(CNode& node, Peer& peer, DataStream& v
 
     // Populate headers.
     const CBlockIndex* block_index = stop_index;
-    for (int i = headers.size() - 1; i >= 0; i--) {
+    for (int i = int(headers.size()) - 1; i >= 0; i--) {
         int height = (i + 1) * CFCHECKPT_INTERVAL;
         block_index = block_index->GetAncestor(height);
 
```
