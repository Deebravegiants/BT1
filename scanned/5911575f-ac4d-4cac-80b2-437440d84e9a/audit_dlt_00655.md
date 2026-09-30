# [?] Merge bitcoin/bitcoin#35872: rpc: avoid descriptor range counter overflow

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoin/bitcoin
Published: 2026-08-06
Source: https://github.com/bitcoin/bitcoin/commit/b388674acf06e9cf64788375817737578358367f
Type: security-commit

## Details
Merge bitcoin/bitcoin#35872: rpc: avoid descriptor range counter overflow

264555af3cc2ab2919e49e7dea3f8066b9336020 rpc: avoid descriptor range counter overflow (Lőrinc)
143a13fb2bd190e50c26bb5582c6c0a2af17867a test: characterize descriptor range endpoint (Lőrinc)

Pull request description:

  **Problem:** The authenticated `scantxoutset`, `scanblocks`, `getdescriptoractivity`, `utxoupdatepsbt`, and `descriptorprocesspsbt` RPCs share a descriptor expansion helper that iterates inclusive `int64_t` ranges with an `int` counter.
  A ranged descriptor with an explicit `[begin, end]` range ending at `2^31 - 1` expands that valid position, then overflows when advancing the counter to exit the loop.
  Trap-enabled builds terminate, while other builds invoke undefined behavior.

  **Fix:** Use `int64_t` for loop control so the one-past-the-end value is representable and every position passed to `Descriptor::Expand()` remains within its existing `int` range.

  Related: [#26275](https://github.com/bitcoin/bitcoin/pull/26275) fixed the same endpoint overflow in `deriveaddresses`.

ACKs for top commit:
  achow101:
    ACK 264555af3cc2ab2919e49e7dea3f8066b9336020
  polespinasa:
    ACK 264555af3cc2ab2919e49e7dea3f8066b9336020
  sedited:
    ACK 264555af3cc2ab2919e49e7dea3f8066b9336020

Tree-SHA512: 4326182b5897b6f6672e5f7c7296eafdbb6e3b5ed901d61e8fa2cff9b19d372bb8adb88902368dc520ed400e12dd5264ea68677d9ce0feec76fa2ef55fa0d2f4

## Patch
### src/rpc/util.cpp
```diff
@@ -1364,7 +1364,7 @@ std::vector<CScript> EvalDescriptorStringOrObject(const UniValue& scanobject, Fl
         range.second = 0;
     }
     std::vector<CScript> ret;
-    for (int i = range.first; i <= range.second; ++i) {
+    for (int64_t i = range.first; i <= range.second; ++i) {
         for (const auto& desc : descs) {
             std::vector<CScript> scripts;
             if (!desc->Expand(i, provider, scripts, provider)) {
```

### test/functional/rpc_scantxoutset.py
```diff
@@ -80,6 +80,8 @@ def run_test(self):
         assert_raises_rpc_error(-8, "End of range is too high", self.nodes[0].scantxoutset, "start", [{"desc": "desc", "range": [(2 << 31 + 1) - 1000000, (2 << 31 + 1)]}])
         assert_raises_rpc_error(-8, "Range specified as [begin,end] must not have begin after end", self.nodes[0].scantxoutset, "start", [{"desc": "desc", "range": [2, 1]}])
         assert_raises_rpc_error(-8, "Range is too large", self.nodes[0].scantxoutset, "start", [{"desc": "desc", "range": [0, 1000001]}])
+        range_end = 2**31 - 1
+        assert_equal(self.nodes[0].scantxoutset("start", [{"desc": "combo(tprv8ZgxMBicQKsPd7Uf69XL1XwhmjHopUGep8GuEiJDZmbQz6o58LninorQAfcKZWARbtRtfnLcJ5MQ2AtHcQJCCRUcMRvmDUjyEmNUWwx8UbK/0h/0'/*)", "range": [range_end, range_end]}])['success'], True)
 
         self.log.info("Test extended key derivation.")
         # Run various scans, and verify that the sum of the amounts of the matches corresponds to the expected subset.
```
