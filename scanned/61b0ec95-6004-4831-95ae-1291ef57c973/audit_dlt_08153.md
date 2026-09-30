# [?] Fix nondeterminism in `WalletTests.UpdatedSaplingNoteData`

## Summary
Severity: Unknown
Chain: Zcash
Component: zcash/zcash
Published: 2023-06-01
Source: https://github.com/zcash/zcash/commit/6a3306e34e43457e0e0d453c4b60f8735268b68b
Type: security-commit

## Details
Fix nondeterminism in `WalletTests.UpdatedSaplingNoteData`

## Patch
### src/wallet/gtest/test_wallet.cpp
```diff
@@ -81,17 +81,17 @@ class TestWallet : public CWallet {
     }
 };
 
-std::vector<SaplingOutPoint> SetSaplingNoteData(CWalletTx& wtx) {
+static std::vector<SaplingOutPoint> SetSaplingNoteData(CWalletTx& wtx, uint32_t idx) {
     mapSaplingNoteData_t saplingNoteData;
-    SaplingOutPoint saplingOutPoint = {wtx.GetHash(), 0};
+    SaplingOutPoint saplingOutPoint = {wtx.GetHash(), idx};
     SaplingNoteData saplingNd;
     saplingNoteData[saplingOutPoint] = saplingNd;
     wtx.SetSaplingNoteData(saplingNoteData);
     std::vector<SaplingOutPoint> saplingNotes {saplingOutPoint};
     return saplingNotes;
 }
 
-std::pair<JSOutPoint, SaplingOutPoint> CreateValidBlock(TestWallet& wallet,
+static std::pair<JSOutPoint, SaplingOutPoint> CreateValidBlock(TestWallet& wallet,
                             const libzcash::SproutSpendingKey& sk,
                             const CBlockIndex& index,
                             CBlock& block,
@@ -105,7 +105,7 @@ std::pair<JSOutPoint, SaplingOutPoint> CreateValidBlock(TestWallet& wallet,
     SproutNoteData nd {sk.address(), nullifier};
     noteData[jsoutpt] = nd;
     wtx.SetSproutNoteData(noteData);
-    auto saplingNotes = SetSaplingNoteData(wtx);
+    auto saplingNotes = SetSaplingNoteData(wtx, 0);
     wallet.LoadWalletTx(wtx);
 
     block.vtx.push_back(wtx);
@@ -114,7 +114,7 @@ std::pair<JSOutPoint, SaplingOutPoint> CreateValidBlock(TestWallet& wallet,
     return std::make_pair(jsoutpt, saplingNotes[0]);
 }
 
-std::pair<uint256, uint256> GetWitnessesAndAnchors(
+static std::pair<uint256, uint256> GetWitnessesAndAnchors(
                                 const TestWallet& wallet,
                                 const std::vector<JSOutPoint>& sproutNotes,
                                 const std::vector<SaplingOutPoint>& saplingNotes,
@@ -1349,7 +1349,7 @@ TEST(WalletTests, CachedWitnessesEmptyChain) {
     wtx.SetSproutNoteData(sproutNoteData);
 
     std::vector<JSOutPoint> sproutNotes {jsoutpt, jsoutpt2};
-    std::vector<SaplingOutPoint> saplingNotes = SetSaplingNoteData(wtx);
+    std::vector<SaplingOutPoint> saplingNotes = SetSaplingNoteData(wtx, 0);
 
     std::vector<std::optional<SproutWitness>> sproutWitnesses;
     std::vector<std::optional<SaplingWitness>> saplingWitnesses;
@@ -1460,7 +1460,7 @@ TEST(WalletTests, CachedWitnessesChainTip) {
         SproutNoteData nd {sk.address(), nullifier};
         sproutNoteData[jsoutpt] = nd;
         wtx.SetSproutNoteData(sproutNoteData);
-        std::vector<SaplingOutPoint> saplingNotes = SetSaplingNoteData(wtx);
+        std::vector<SaplingOutPoint> saplingNotes = SetSaplingNoteData(wtx, 0);
         wallet.LoadWalletTx(wtx);
 
         std::vector<JSOutPoint> sproutNotes {jsoutpt};
@@ -1570,7 +1570,7 @@ TEST(WalletTests, CachedWitnessesDecrementFirst) {
         SproutNoteData nd {sk.address(), nullifier};
         noteData[jsoutpt] = nd;
         wtx.SetSproutNoteData(noteData);
-        std::vector<SaplingOutPoint> saplingNotes = SetSaplingNoteData(wtx);
+        std::vector<SaplingOutPoint> saplingNotes = SetSaplingNoteData(wtx, 0);
         wallet.LoadWalletTx(wtx);
 
         std::vector<JSOutPoint> sproutNotes {jsoutpt};
@@ -1712,7 +1712,7 @@ TEST(WalletTests, ClearNoteWitnessCache) {
     SproutNoteData nd {sk.address(), nullifier};
     noteData[jsoutpt] = nd;
     wtx.SetSproutNoteData(noteData);
-    auto saplingNotes = SetSaplingNoteData(wtx);
+    auto saplingNotes = SetSaplingNoteData(wtx, 0);
 
     // Pretend we mined the tx by adding a fake witness
     SproutMerkleTree sproutTree;
@@ -1913,7 +1913,7 @@ TEST(WalletTests, SetBestChainIgnoresTxsWithoutShieldedData) {
     mtxSapling.nVersionGroupId = SAPLING_VERSION_GROUP_ID;
     mtxSapling.saplingBundle = sapling::test_only_invalid_bundle(0, 1, 0);
     CWalletTx wtxSapling {nullptr, mtxSapling};
-    SetSaplingNoteData(wtxSapling);
+    SetSaplingNoteData(wtxSapling, 0);
     wallet.LoadWalletTx(wtxSapling);
 
     // Generate a fake Sapling transaction that would only involve our transparent addresses
@@ -2107,13 +2107,16 @@ TEST(WalletTests, UpdatedSaplingNoteData) {
     CWalletTx wtx2 = wtx;
     auto saplingNoteData2 = wallet.FindMySaplingNotes(Params(), wtx2, chainActive.Height()).first;
     ASSERT_EQ(saplingNoteData2.size(), 2);
+
+    // Identify the index of the non-change note
+    auto sentIndex = sopChange.n == 0 ? 1 : 0;
     wtx2.SetSaplingNoteData(saplingNoteData2);
 
     // The payment note has not been witnessed yet, so let's fake the witness.
     // The hash of wtx2 is unchanged since it's a copy of wtx, and since wtx's
     // outpoints are in random order, we assign sopNew's index to whichever
     // sopChange didn't use.
-    SaplingOutPoint sopNew(wtx2.GetHash(), sopChange.n == 0 ? 1 : 0);
+    SaplingOutPoint sopNew(wtx2.GetHash(), sentIndex);
     wtx2.mapSaplingNoteData[sopNew].witnesses.push_front(frontiers.sapling.witness());
     wtx2.mapSaplingNoteData[sopNew].witnessHeight = 0;
 
@@ -2134,15 +2137,25 @@ TEST(WalletTests, UpdatedSaplingNoteData) {
     // EXPECT_EQ(wtx.mapSaplingNoteData, wtx2.mapSaplingNoteData);
     // because nullifiers (if part of == comparator) have not all been computed
     // Also note that mapwallet[hash] is not updated with the updated wtx.
-   // wtx = wallet.mapWallet[hash];
+    // wtx = wallet.mapWallet[hash];
 
-    EXPECT_EQ(2, wtx.mapSaplingNoteData.size());
     EXPECT_EQ(2, wtx2.mapSaplingNoteData.size());
+    EXPECT_EQ(0, wtx2.mapSaplingNoteData[sopChange].witnesses.size());
+
+    EXPECT_EQ(2, wtx.mapSaplingNoteData.size());
     // wtx copied over the fake witness from wtx2 for the payment output
-    EXPECT_EQ(wtx.mapSaplingNoteData[sopNew].witnesses.front(), wtx2.mapSaplingNoteData[sopNew].witnesses.front());
+    EXPECT_EQ(
+        wtx.mapSaplingNoteData[sopNew].witnesses.front(),
+        wtx2.mapSaplingNoteData[sopNew].witnesses.front()
+    );
     // wtx2 never had its change output witnessed even though it has been in wtx
-    EXPECT_EQ(0, wtx2.mapSaplingNoteData[sopChange].witnesses.size());
-    EXPECT_EQ(wtx.mapSaplingNoteData[sopChange].witnesses.front(), frontiers.sapling.witness());
+    EXPECT_EQ(wtx.mapSaplingNoteData[sopChange].witnesses.front().root(), frontiers.sapling.witness().root());
+    if (sopChange.n == 1) {
+        EXPECT_EQ(wtx.mapSaplingNoteData[sopChange].witnesses.front(), frontiers.sapling.witness());
+    } else {
+        EXPECT_FALSE(wtx.mapSaplingNoteData[sopChange].witnesses.front() == frontiers.sapling.witness());
+    }
+
 
     // Tear down
     chainActive.SetTip(NULL);
```
