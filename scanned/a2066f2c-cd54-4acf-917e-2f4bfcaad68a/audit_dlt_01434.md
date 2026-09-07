# [?] Merge bitcoin/bitcoin#33956: net: fix use-after-free with v2->v1 reconnection logic

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoin/bitcoin
Published: 2025-12-05
Source: https://github.com/bitcoin/bitcoin/commit/0c9ab0f8f8c85719ff3aa4aefe3198cd2f8d63d1
Type: security-commit

## Details
Merge bitcoin/bitcoin#33956: net: fix use-after-free with v2->v1 reconnection logic

167df7a98c8514da6979d45e58fcdcbd0733b8fe net: fix use-after-free with v2->v1 reconnection logic (Eugene Siegel)

Pull request description:

  `CConnman::Stop()` resets `semOutbound`, yet `m_reconnections` is not cleared in `Stop`. Each `ReconnectionInfo` contains a `grant` member that points to the memory that `semOutbound` pointed to and `~CConnman` will attempt to access the grant field (memory that was already freed) when destroying `m_reconnections`. Fix this by calling `m_reconnections.clear()` in `CConnman::Stop()` and add appropriate annotations.

  I was able to reproduce the original issue https://github.com/bitcoin/bitcoin/issues/33615 with the following diff by randomly stopping my node while it was attempting to reconnect (and verified that this patch fixes the issue, at least in my ~40-50 runs):
  <details>
  <summary> diff </summary>

  ```diff
  diff --git a/src/net.cpp b/src/net.cpp
  index ef1c63044a..9c1d161d8b 100644
  --- a/src/net.cpp
  +++ b/src/net.cpp
  @@ -1918,8 +1918,8 @@ void CConnman::DisconnectNodes()
       {
           LOCK(m_nodes_mutex);

  -        const bool network_active{fNetworkActive};
  -        if (!network_active) {
  +//        const bool network_active{fNetworkActive};
  +//        if (!network_active) {
               // Disconnect any connected nodes
               for (CNode* pnode : m_nodes) {
                   if (!pnode->fDisconnect) {
  @@ -1927,7 +1927,7 @@ void CConnman::DisconnectNodes()
                       pnode->fDisconnect = true;
                   }
               }
  -        }
  +//        }

           // Disconnect unused nodes
           std::vector<CNode*> nodes_copy = m_nodes;
  @@ -1941,7 +1941,7 @@ void CConnman::DisconnectNodes()
```

_Trimmed to 38 lines — full report: https://github.com/bitcoin/bitcoin/commit/0c9ab0f8f8c85719ff3aa4aefe3198cd2f8d63d1_
