# [?] net_processing: Fix overflow and limit vInv reserve size to MAX_INV_SZ

## Summary
Severity: Unknown
Chain: Bitcoin Cash
Component: bitcoin-cash-node/bitcoin-cash-node
Published: 2021-12-13
Source: https://github.com/bitcoin-cash-node/bitcoin-cash-node/commit/1d39a84f384be0fae3a4da7d40cbbc56534c23cc
Type: security-commit

## Details
net_processing: Fix overflow and limit vInv reserve size to MAX_INV_SZ

## Patch
### src/net_processing.cpp
```diff
@@ -40,6 +40,7 @@
 #include <validation.h>
 #include <validationinterface.h>
 
+#include <cmath>
 #include <memory>
 #include <stdexcept>
 #include <type_traits>
@@ -4586,12 +4587,25 @@ bool PeerLogicValidation::SendMessages(const Config &config, CNode *pto,
     {
         LOCK(pto->cs_inventory);
 
-        // txs per broadcast = (tx/sec/MB) * (block_bytes) * (ms/broadcast) * (1 sec/1000 ms) * (1 MB/1000000 bytes) (rounded up)
         const uint64_t invBroadcastInterval = config.GetInvBroadcastInterval();
-        const uint64_t nMaxBroadcasts = (config.GetInvBroadcastRate() * config.GetExcessiveBlockSize()
-                                         * std::max(invBroadcastInterval, uint64_t{1}) + (1000 * 1000000 - 1))
-                                        / 1000 / 1000000;
-        vInv.reserve(std::max<size_t>(pto->vInventoryBlockToSend.size(), nMaxBroadcasts));
+        const uint64_t nMaxBroadcasts = [&]{
+            // txs per broadcast = (tx/sec/MB) * (block_bytes) * (ms/broadcast) * (1 sec/1000 ms) * (1 MB/1000000 bytes) (rounded up)
+            const uint64_t txPerSec = config.GetInvBroadcastRate()
+                                      // rate in tx per sec is a function of the block size in MB (rounded up)
+                                      * ((config.GetExcessiveBlockSize() + (ONE_MEGABYTE - 1)) / ONE_MEGABYTE);
+            const uint64_t intervalNonZero = std::max(invBroadcastInterval, uint64_t{1});
+            return std::ceil(txPerSec * (intervalNonZero / 1000.0));
+        }();
+        {
+            // reserve memory, limiting it to what we anticipate to send, up to a cap of MAX_INV_SZ
+            const uint64_t nTxsToSend = [&]{
+                LOCK(pto->cs_filter);
+                return pto->fRelayTxes ? pto->setInventoryTxToSend.size() : 0;
+            }();
+            const uint64_t nBlocksToSend = pto->vInventoryBlockToSend.size();
+            vInv.reserve(std::min(uint64_t(MAX_INV_SZ), /* we never send more that MAX_INV_SZ items at a time */
+                                  std::max(std::min(nMaxBroadcasts, nTxsToSend), nBlocksToSend)));
+        }
 
         // Add blocks
         for (const BlockHash &hash : pto->vInventoryBlockToSend) {
```
