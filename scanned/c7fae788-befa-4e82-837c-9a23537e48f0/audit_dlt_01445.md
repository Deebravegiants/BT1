# [?] Merge bitcoin/bitcoin#33475: bugfix: miner: fix `addPackageTxs` unsigned integer overflow

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoin/bitcoin
Published: 2025-09-25
Source: https://github.com/bitcoin/bitcoin/commit/05d984b1a4fb6402d93a436203e986cde60fd99f
Type: security-commit

## Details
Merge bitcoin/bitcoin#33475: bugfix: miner: fix `addPackageTxs` unsigned integer overflow

b807dfcdc5929c314d43b790c9e705d5bf0a86e8 miner: fix `addPackageTxs` unsigned integer overflow (ismaelsadeeq)

Pull request description:

  This PR fixes an unsigned integer overflow in the `addPackageTxs` method of the `BlockAssembler`.

  The overflow is a rare edge case that might occur on master when a miner reserves 2000 WU and wants to create an block to be empty.

  i.e, by starting with `-blockmaxweight=2000`, `-blockreservedweight=2000`, or just `blockmaxweight=2000`, and then calling the mining interface `createNewBlock` with `blockReservedWeight` set to `2000`.

  Instead of bailing out after going through transactions equivalent to `MAX_CONSECUTIVE_FAILURES`, the loop never breaks until all mempool transactions are visited.

  See https://github.com/bitcoin/bitcoin/pull/33421#issuecomment-3324859282

  The fix avoids the overflow by using addition instead adding `BLOCK_FULL_ENOUGH_WEIGHT_DELTA` to the block weight and comparing it with `m_options.nBlockMaxWeight`.

  Another alternative that preserves the same structure is to use `static_cast`. See https://github.com/bitcoin/bitcoin/pull/33421/commits/c9530cf35d351628eea4992c66fc1df548d1b580.

  This fix can be tested by cherry-picking the commits from #33421 without the static cast fix and running:

  ```bash
  echo "AQAAAAAAA
  AAnJycnAAAAAAAAAAAAAAAAAA" | base64 --decode > miner.crash

  FUZZ=block_template_cache ./build_fuzz/bin/fuzz miner.crash
  ```

  ---

  This is part of a larger inconsistency in how size/weight is represented in the codebase. It may be worth defining a dedicated type for size/weight.

ACKs for top commit:
  glozow:
    nice, utACK b807dfcdc5929c314d43b790c9e705d5bf0a86e8
  furszy:
    Code ACK b807dfcdc5929c314d43b790c9e705d5bf0a86e8

Tree-SHA512: c1d2f7e500f9b0624a4c22a146921a1644017065e6c94d0c5027486392321f5de26c61751a24765e025e45b34c535adfd6d0e2ac809dea6846b99f37d13043c9

### src/node/miner.cpp
```diff
@@ -397,8 +397,8 @@ void BlockAssembler::addPackageTxs(int& nPackagesSelected, int& nDescendantsUpda
 
             ++nConsecutiveFailed;
 
-            if (nConsecutiveFailed > MAX_CONSECUTIVE_FAILURES && nBlockWeight >
-                    m_options.nBlockMaxWeight - BLOCK_FULL_ENOUGH_WEIGHT_DELTA) {
+            if (nConsecutiveFailed > MAX_CONSECUTIVE_FAILURES && nBlockWeight +
+                    BLOCK_FULL_ENOUGH_WEIGHT_DELTA > m_options.nBlockMaxWeight) {
                 // Give up if we're close to full and haven't succeeded in a while
                 break;
             }
```
