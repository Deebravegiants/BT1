# [?] Block storage: Fix OOM crash when block is larger than block file size

## Summary
Severity: Unknown
Chain: Bitcoin Cash
Component: bitcoin-cash-node/bitcoin-cash-node
Published: 2020-11-15
Source: https://github.com/bitcoin-cash-node/bitcoin-cash-node/commit/393e46f7c934bdbcdeb415b6dcc1441eecf5ca51
Type: security-commit

## Details
Block storage: Fix OOM crash when block is larger than block file size

Summary
---

When a received block exceeded the `MAX_BLOCKFILE_SIZE` limit, the code
in `FindBlockPos` would just loop forever, adding another element to
`vinfoBlockFile` each time, eventually causing an allocation failure or
the OOM killer killing the process.

The problem is fixed by checking the current `CBlockFileInfo`'s `nSize`
for zero. This makes the code behave the same as before if the block
does not exceed `MAX_BLOCKFILE_SIZE`, if it does exceed it, a file
larger than the maximum is created.

Test plan
---

* ninja check
* sync scalenet past block height 16809, it should not crash

## Patch
### src/validation.cpp
```diff
@@ -3449,7 +3449,8 @@ static bool FindBlockPos(FlatFilePos &pos, unsigned int nAddSize,
     }
 
     if (!fKnown) {
-        while (vinfoBlockFile[nFile].nSize + nAddSize >= MAX_BLOCKFILE_SIZE) {
+        while (vinfoBlockFile[nFile].nSize > 0 &&
+               vinfoBlockFile[nFile].nSize + nAddSize >= MAX_BLOCKFILE_SIZE) {
             nFile++;
             if (vinfoBlockFile.size() <= nFile) {
                 vinfoBlockFile.resize(nFile + 1);
```
