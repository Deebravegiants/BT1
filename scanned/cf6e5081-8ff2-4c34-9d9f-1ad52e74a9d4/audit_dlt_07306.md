# [?] Avoid overflow in ConservationOfLumensTests

## Summary
Severity: Unknown
Chain: Stellar
Component: stellar/stellar-core
Published: 2021-03-01
Source: https://github.com/stellar/stellar-core/commit/adecddad268adc6adea8cdc15b3406359c1e87d4
Type: security-commit

## Details
Avoid overflow in ConservationOfLumensTests

Prevent the "Account balances unchanged without inflation"
test from adjusting LedgerHeader::totalCoins when it doesn't
mean to be doing so.

Also add a REQUIRE() to try to catch any further such
overflows.

## Patch
### src/invariant/test/ConservationOfLumensTests.cpp
```diff
@@ -43,7 +43,7 @@ getCoinsAboveReserve(std::vector<LedgerEntry> const& entries, Application& app)
 
 std::vector<LedgerEntry>
 updateBalances(std::vector<LedgerEntry> entries, Application& app,
-               int64_t netChange)
+               int64_t netChange, bool updateTotalCoins)
 {
     int64_t initialCoins = getTotalBalance(entries);
     int64_t pool = netChange + getCoinsAboveReserve(entries, app);
@@ -79,9 +79,18 @@ updateBalances(std::vector<LedgerEntry> entries, Application& app,
     auto finalCoins = getTotalBalance(entries);
     REQUIRE(initialCoins + netChange == finalCoins);
 
-    LedgerTxn ltx(app.getLedgerTxnRoot());
-    ltx.loadHeader().current().totalCoins += netChange;
-    ltx.commit();
+    if (updateTotalCoins)
+    {
+        LedgerTxn ltx(app.getLedgerTxnRoot());
+        auto& current = ltx.loadHeader().current();
+        REQUIRE(current.totalCoins >= 0);
+        if (netChange > 0)
+        {
+            REQUIRE(current.totalCoins <= INT64_MAX - netChange);
+        }
+        current.totalCoins += netChange;
+        ltx.commit();
+    }
     return entries;
 }
 
@@ -99,7 +108,7 @@ updateBalances(std::vector<LedgerEntry> const& entries, Application& app)
     std::uniform_int_distribution<int64_t> dist(totalCoins - coinsAboveReserve,
                                                 INT64_MAX);
     int64_t newTotalCoins = dist(gRandomEngine);
-    return updateBalances(entries, app, newTotalCoins - totalCoins);
+    return updateBalances(entries, app, newTotalCoins - totalCoins, true);
 }
 
 TEST_CASE("Total coins change without inflation",
@@ -195,7 +204,7 @@ TEST_CASE("Account balances unchanged without inflation",
             REQUIRE(!store(*app, updates));
         }
 
-        auto entries2 = updateBalances(entries1, *app, 0);
+        auto entries2 = updateBalances(entries1, *app, 0, false);
         {
             auto updates = makeUpdateList(entries2, entries1);
             REQUIRE(store(*app, updates));
@@ -205,7 +214,7 @@ TEST_CASE("Account balances unchanged without inflation",
         std::vector<LedgerEntry> entries3(entries2.begin(), keepEnd);
         std::vector<LedgerEntry> toDelete(keepEnd, entries2.end());
         int64_t balanceToDelete = getTotalBalance(toDelete);
-        auto entries4 = updateBalances(entries3, *app, balanceToDelete);
+        auto entries4 = updateBalances(entries3, *app, balanceToDelete, false);
         {
             auto updates = makeUpdateList(entries4, entries3);
             auto updates2 = makeUpdateList(nullptr, toDelete);
@@ -273,7 +282,7 @@ TEST_CASE("Inflation changes are consistent",
                               InvariantDoesNotHold);
         }
 
-        auto entries2 = updateBalances(entries1, *app, inflationAmount);
+        auto entries2 = updateBalances(entries1, *app, inflationAmount, true);
         {
             LedgerTxn ltx(app->getLedgerTxnRoot());
             ltx.loadHeader().current().feePool += deltaFeePool;
```
