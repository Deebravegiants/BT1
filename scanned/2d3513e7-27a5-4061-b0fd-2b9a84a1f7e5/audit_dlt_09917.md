# [?] Merge pull request #566 from hyeonLewis/prevent-underflow

## Summary
Severity: Unknown
Chain: Kaia
Component: kaiachain/kaia
Published: 2025-10-05
Source: https://github.com/kaiachain/kaia/commit/71804915bcc528d7b160d744371769e19cc35b08
Type: security-commit

## Details
Merge pull request #566 from hyeonLewis/prevent-underflow

contract: Prevent underflow in deposit vault getter

## Patch
### contracts/contracts/system_contracts/auction/AuctionDepositVault.sol
```diff
@@ -287,6 +287,7 @@ contract AuctionDepositVault is IAuctionDepositVault, AuctionError, Ownable {
                 ? totalAddresses
                 : start + limit;
         }
+        if (start >= end) revert InvalidRange();
 
         searchers = new address[](end - start);
         for (uint256 i = start; i < end; i++) {
@@ -322,6 +323,7 @@ contract AuctionDepositVault is IAuctionDepositVault, AuctionError, Ownable {
                 ? totalAddresses
                 : start + limit;
         }
+        if (start >= end) revert InvalidRange();
 
         INonce entryPoint = INonce(_getAuctionEntryPointAddress());
 
```

### contracts/contracts/system_contracts/auction/AuctionError.sol
```diff
@@ -25,6 +25,7 @@ contract AuctionError {
     }
 
     error ZeroAddress();
+    error InvalidRange();
 
     error OnlyProposer();
     error EmptyDepositVault();
```

### contracts/test/Auction/auctionDepositVault.test.ts
```diff
@@ -486,6 +486,13 @@ describe("AuctionDepositVault", () => {
         fixture.user3.address,
       ]);
     });
+    it("#getDepositAddrs: invalid range", async () => {
+      const { auctionDepositVault } = fixture;
+
+      await expect(
+        auctionDepositVault.getDepositAddrs(3, 0)
+      ).to.be.revertedWithCustomError(auctionDepositVault, "InvalidRange");
+    });
     it("#isMinDepositOver: success", async () => {
       const { auctionDepositVault, user1 } = fixture;
 
@@ -536,5 +543,12 @@ describe("AuctionDepositVault", () => {
         [0, 0],
       ]);
     });
+    it("#getAllAddrsOverMinDeposit: invalid range", async () => {
+      const { auctionDepositVault } = fixture;
+
+      await expect(
+        auctionDepositVault.getAllAddrsOverMinDeposit(3, 0)
+      ).to.be.revertedWithCustomError(auctionDepositVault, "InvalidRange");
+    });
   });
 });
```
