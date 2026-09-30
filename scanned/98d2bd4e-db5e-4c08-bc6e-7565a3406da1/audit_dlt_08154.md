# [?] Fix a nondeterministic error in wallet tests caused by output shuffling.

## Summary
Severity: Unknown
Chain: Zcash
Component: zcash/zcash
Published: 2023-05-31
Source: https://github.com/zcash/zcash/commit/09723a9e00c9921ddc3782a8e7d7b8e2dfcd4dfd
Type: security-commit

## Details
Fix a nondeterministic error in wallet tests caused by output shuffling.

## Patch
### src/wallet/gtest/test_wallet.cpp
```diff
@@ -2086,7 +2086,9 @@ TEST(WalletTests, UpdatedSaplingNoteData) {
 
     // Simulate SyncTransaction which calls AddToWalletIfInvolvingMe
     auto saplingNoteData = wallet.FindMySaplingNotes(Params(), wtx, chainActive.Height()).first;
-    ASSERT_TRUE(saplingNoteData.size() == 1); // wallet only has key for change output
+    ASSERT_EQ(saplingNoteData.size(), 1); // wallet only has key for change output
+    SaplingOutPoint sopChange = saplingNoteData.begin()->first;
+
     wtx.SetSaplingNoteData(saplingNoteData);
     wtx.SetMerkleBranch(block);
     wallet.LoadWalletTx(wtx);
@@ -2104,24 +2106,26 @@ TEST(WalletTests, UpdatedSaplingNoteData) {
     ASSERT_TRUE(wallet.HaveSaplingSpendingKey(extfvk2));
     CWalletTx wtx2 = wtx;
     auto saplingNoteData2 = wallet.FindMySaplingNotes(Params(), wtx2, chainActive.Height()).first;
-    ASSERT_TRUE(saplingNoteData2.size() == 2);
+    ASSERT_EQ(saplingNoteData2.size(), 2);
     wtx2.SetSaplingNoteData(saplingNoteData2);
 
     // The payment note has not been witnessed yet, so let's fake the witness.
-    SaplingOutPoint sop0(wtx2.GetHash(), 0);
-    SaplingOutPoint sop1(wtx2.GetHash(), 1);
-    wtx2.mapSaplingNoteData[sop0].witnesses.push_front(frontiers.sapling.witness());
-    wtx2.mapSaplingNoteData[sop0].witnessHeight = 0;
+    // The hash of wtx2 is unchanged since it's a copy of wtx, and since wtx's
+    // outpoints are in random order, we assign sopNew's index to whichever
+    // sopChange didn't use.
+    SaplingOutPoint sopNew(wtx2.GetHash(), sopChange.n == 0 ? 1 : 0);
+    wtx2.mapSaplingNoteData[sopNew].witnesses.push_front(frontiers.sapling.witness());
+    wtx2.mapSaplingNoteData[sopNew].witnessHeight = 0;
 
     // The txs are different as wtx is aware of just the change output,
     // whereas wtx2 is aware of both payment and change outputs.
     EXPECT_NE(wtx.mapSaplingNoteData, wtx2.mapSaplingNoteData);
     EXPECT_EQ(1, wtx.mapSaplingNoteData.size());
-    EXPECT_EQ(1, wtx.mapSaplingNoteData[sop1].witnesses.size());    // wtx has witness for change
+    EXPECT_EQ(1, wtx.mapSaplingNoteData[sopChange].witnesses.size());    // wtx has witness for change
 
     EXPECT_EQ(2, wtx2.mapSaplingNoteData.size());
-    EXPECT_EQ(1, wtx2.mapSaplingNoteData[sop0].witnesses.size());    // wtx2 has fake witness for payment output
-    EXPECT_EQ(0, wtx2.mapSaplingNoteData[sop1].witnesses.size());    // wtx2 never had incrementnotewitness called
+    EXPECT_EQ(1, wtx2.mapSaplingNoteData[sopNew].witnesses.size());      // wtx2 has fake witness for payment output
+    EXPECT_EQ(0, wtx2.mapSaplingNoteData[sopChange].witnesses.size());   // wtx2 never had incrementnotewitness called
 
     // After updating, they should be the same
     EXPECT_TRUE(wallet.UpdatedNoteData(wtx2, wtx));
@@ -2135,10 +2139,10 @@ TEST(WalletTests, UpdatedSaplingNoteData) {
     EXPECT_EQ(2, wtx.mapSaplingNoteData.size());
     EXPECT_EQ(2, wtx2.mapSaplingNoteData.size());
     // wtx copied over the fake witness from wtx2 for the payment output
-    EXPECT_EQ(wtx.mapSaplingNoteData[sop0].witnesses.front(), wtx2.mapSaplingNoteData[sop0].witnesses.front());
+    EXPECT_EQ(wtx.mapSaplingNoteData[sopNew].witnesses.front(), wtx2.mapSaplingNoteData[sopNew].witnesses.front());
     // wtx2 never had its change output witnessed even though it has been in wtx
-    EXPECT_EQ(0, wtx2.mapSaplingNoteData[sop1].witnesses.size());
-    EXPECT_EQ(wtx.mapSaplingNoteData[sop1].witnesses.front(), frontiers.sapling.witness());
+    EXPECT_EQ(0, wtx2.mapSaplingNoteData[sopChange].witnesses.size());
+    EXPECT_EQ(wtx.mapSaplingNoteData[sopChange].witnesses.front(), frontiers.sapling.witness());
 
     // Tear down
     chainActive.SetTip(NULL);
```
