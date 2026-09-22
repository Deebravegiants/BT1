# [M] High gas consumpsiont on

## Summary
Severity: Medium
Reporter: 0x4non
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128-L169
Type: audit-issue

## Details
# High gas consumpsiont on

## Summary

Minting NFT could be really high gas consumption, especially on mainnet, that why im adding this issue, in this report i will demonstrate how to lower up to 50% percent gas consumption on minting.

## Vulnerability Detail

High gas consumption due usage of ERC721Enumerable.

## Impact

High cost on minting.

After mitigation:

```bash
Test result: ok. 13 passed; 0 failed; 0 skipped; finished in 944.63ms
Ran 2 test suites: 19 tests passed, 0 failed, 0 skipped (19 total tests)
testMintMultipleUnderpayShouldFail() (gas: 0 (0.000%)) 
testMintSingleUnderpayShouldFail() (gas: 0 (0.000%)) 
testMintBeforeStartShouldFail() (gas: 22 (0.160%)) 
testConstructor() (gas: -2144 (-8.016%)) 
testSetBaseURI() (gas: -2355 (-12.087%)) 
testMintFromNonMinterShouldFail() (gas: -2347 (-20.276%)) 
testSetBaseURIFromNonUriSetterShouldFail() (gas: -2409 (-20.319%)) 
testMintSingleOverypay() (gas: -54087 (-23.465%)) 
testMintAfterEnd() (gas: -54087 (-23.531%)) 
testClaimProceeds() (gas: -54043 (-23.643%)) 
testMintSingleExactAmount() (gas: -54109 (-24.542%)) 
testClaimProceedsFromNonOwnerShouldFail() (gas: -54043 (-24.847%)) 
testTokenUri() (gas: -51722 (-38.178%)) 
testMint() (gas: -51799 (-39.103%)) 
testConstructor() (gas: -15420 (-44.024%)) 
testRunAuction() (gas: -699414078 (-44.861%)) 
testMintMoreThanCapShouldFail() (gas: -699634056 (-45.691%)) 
testMintMultiple() (gas: -236067 (-51.553%)) 
testMintMoreThanCapPerAddressShouldFail() (gas: -326793 (-57.144%)) 
Overall gas change: -1400009537 (-45.266%)
```

## Code Snippet

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128-L169

## Tool used

Manual Review

## Recommendation

```diff
diff --git a/dutch-nft/src/MeritDutchAuction.sol b/dutch-nft/src/MeritDutchAuction.sol
index 21a2281..423069e 100644
--- a/dutch-nft/src/MeritDutchAuction.sol
+++ b/dutch-nft/src/MeritDutchAuction.sol
@@ -25,7 +25,7 @@ contract MeritDutchAuction is Ownable {
     uint256 public immutable stepSize;
 
     // NFT contract which gets minted to users during the auction. Contract should allow the auction contract to mint NFTs
-    MeritNFT public nft;
+    MeritNFT public immutable nft;
 
     // Amount of NFTs minted
     uint256 public minted;
@@ -84,15 +84,8 @@ contract MeritDutchAuction is Ownable {
         startTime = startTime_;
         endTime = endTime_;
         stepSize = stepSize_;
-    }
 
-    /// @notice Sets the NFT contract address, can only be called once, only calable by owner
-    /// @param nft_ Address of the NFT contract
-    function setNFT(address nft_) external onlyOwner {
-        // Can only be set once
-        require(address(nft) == address(0), "NFT already set");
-        // NFT contract must allow this contract to mint NFTs
-        nft = MeritNFT(nft_);
+        nft = new MeritNFT("https://example.com/", msg.sender, address(this));
     }
 
     /// @notice Returns the current price
@@ -126,6 +119,9 @@ contract MeritDutchAuction is Ownable {
     /// @notice Mints NFTs, can only be called during the auction or after the auction has ended and the price has reached the end price
     /// @param amount Amount of NFTs to mint
     function mint(uint256 amount) external payable {
+        // @audit missing require, amount > 0 this will let bad actor bypass the mint, and emit a "MINTED" event without having mint
+        // @audit missing require to ensure that NFT collection has been set
+        // @audit transaction should have a deadline to ensure minter wont pay more than he wants to
         // Checks
         // Cache mintedBefore to save on sloads
         uint256 mintedBefore = minted;
@@ -152,12 +148,8 @@ contract MeritDutchAuction is Ownable {
         // Update amount of ETH raised
         totalRaised += totalPaid;
 
-        // Interactions
-        for(uint256 i = 0; i < amount; i++) {
-            // Mint the amount of NFTs to the sender
-            nft.mint(mintedBefore + i + 1, msg.sender);
-        }
-
+        nft.mint(msg.sender, amount);
+        
         if(msg.value > totalPaid) {
             // If too much ETH was sent, refund the difference
             (bool success, ) = payable(msg.sender).call{value: msg.value - totalPaid}(bytes(""));
diff --git a/dutch-nft/src/MeritNFT.sol b/dutch-nft/src/MeritNFT.sol
index bb862d0..208476f 100644
--- a/dutch-nft/src/MeritNFT.sol
+++ b/dutch-nft/src/MeritNFT.sol
@@ -2,12 +2,11 @@
 pragma solidity ^0.8.13;
 
 
-import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
-import "@openzeppelin/contracts/access/AccessControlEnumerable.sol";
+import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
 import "@openzeppelin/contracts/utils/Strings.sol";
 
 
-contract MeritNFT is ERC721Enumerable, AccessControlEnumerable {
+contract MeritNFT is ERC721 {
     using Strings for uint256;
 
     // Emitted when a non minter calls minter only function
@@ -15,56 +14,46 @@ contract MeritNFT is ERC721Enumerable, AccessControlEnumerable {
     // Emitted when a non uri setter calls uri setter only function
     error OnlyURISetter();
 
-    // Role for minters
-    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
-    // Role for setting the baseURI
-    bytes32 public constant URI_SETTER = keccak256("URI_SETTER");
+    uint256 public totalSupply;
+
     // Prefix for the tokenURI. tokenURI = baseTokenURI + tokenId + .json
     string internal baseTokenURI_;
 
-    // Modifier for minter only functions
-    modifier onlyMinter {
-        if(!hasRole(MINTER_ROLE, msg.sender)) {
-            revert OnlyMinterError();
-        }
-        _;
-    }
-
-    // Modifier for uri setter only functions
-    modifier onlyUriSetter {
-        if(!hasRole(URI_SETTER, msg.sender)) {
-            revert OnlyURISetter();
-        }
-        _;
-    }
+    address immutable minter;
+    address immutable uriSetter;
 
     /// @notice Constructor
-    /// @param _name The name of the NFT
-    /// @param _symbol Symbol aka ticker
     /// @param _baseTokenURI Prepends the tokenId for the tokenURI
     constructor(
-        string memory _name,
-        string memory _symbol,
         string memory _baseTokenURI,
         address _uriSetter,
         address _minter
-    ) ERC721(_name, _symbol) {
+    ) ERC721("Merit NFT", "MERIT") {
         baseTokenURI_ = _baseTokenURI;
-        _setupRole(URI_SETTER, _uriSetter);
-        _setupRole(MINTER_ROLE, _minter);
+        uriSetter = _uriSetter;
+        minter = _minter;
     }
 
-
     /// @notice Mints an NFT. Can only be called by an address with the minter role and tokenId must be unique
-    /// @param _tokenId Id of the token
     /// @param _receiver Address receiving the NFT
-    function mint(uint256 _tokenId, address _receiver) external onlyMinter {
-        _mint(_receiver, _tokenId);
+    function mint(address _receiver, uint256 _amount) external {
+        if(_amount == 0) revert("Amount must be greater than 0");
+        if(msg.sender != minter) revert OnlyMinterError();
+        uint256 _newSupply = totalSupply;
+
+        unchecked {
+            for(uint256 i; i < _amount; ++i) {
+                _mint(_receiver, ++_newSupply); // @audit if you use _safeMint, add non reentrancy guard
+            }
+        }
+
+        totalSupply = _newSupply;
     }
 
     /// @notice Sets the base token URI. Can only be called by an address with the default admin role
     /// @param _newBaseURI New baseURI
-    function setBaseURI(string memory _newBaseURI) external onlyUriSetter {
+    function setBaseURI(string memory _newBaseURI) external {
+        if(msg.sender != uriSetter) revert OnlyURISetter();
         baseTokenURI_ = _newBaseURI;
     }
 
@@ -79,18 +68,6 @@ contract MeritNFT is ERC721Enumerable, AccessControlEnumerable {
         return _baseURI();
     }
 
-    /// @notice Signals support for a given interface
-    /// @param interfaceId 4bytes signature of the interface
-    function supportsInterface(bytes4 interfaceId)
-        public
-        view
-        virtual
-        override(AccessControlEnumerable, ERC721Enumerable)
-        returns (bool)
-    {
-        return super.supportsInterface(interfaceId);
-    }
-
     /**
      * @dev See {IERC721Metadata-tokenURI}.
      */
diff --git a/dutch-nft/test/MeritDutchAuction.t.sol b/dutch-nft/test/MeritDutchAuction.t.sol
index 0b40fdc..3b8a15d 100644
--- a/dutch-nft/test/MeritDutchAuction.t.sol
+++ b/dutch-nft/test/MeritDutchAuction.t.sol
@@ -41,8 +41,7 @@ contract MeritDutchAuctionTest is Test {
             STEP_SIZE
         );
 
-        nft = new MeritNFT(NAME, SYMBOL, BASE_URI, uriSetter, address(auction));
-        auction.setNFT(address(nft));
+        nft = auction.nft();
 
         // Gift eth to test addresses
         vm.deal(wallet1, 1000000e18);
@@ -64,35 +63,6 @@ contract MeritDutchAuctionTest is Test {
         assertEq(auction.owner(), owner);
     }
 
-    function testSetNFT() public {
-        vm.startPrank(owner);
-        MeritDutchAuction tempAuction = new MeritDutchAuction(
-            START_PRICE,
-            END_PRICE,
-            startTime,
-            endTime,
-            STEP_SIZE
-        );
-
-        tempAuction.setNFT(address(1337));
-        assertEq(address(tempAuction.nft()), address(1337));
-        vm.stopPrank();
-    }
-
-    function setNFTFromNonOwnerShouldFail() public {
-        vm.startPrank(wallet1);
-        vm.expectRevert("Ownable: caller is not the owner");
-        auction.setNFT(address(1337));
-        vm.stopPrank();
-    }
-
-    function setNFTMoreThanOnceShouldFail() public {
-        vm.startPrank(owner);
-        vm.expectRevert("NFT already set");
-        auction.setNFT(address(1337));
-        vm.stopPrank();
-    }
-
     function testMintSingleExactAmount() public {
         vm.startPrank(wallet1);
         vm.warp(startTime);
@@ -213,14 +183,13 @@ contract MeritDutchAuctionTest is Test {
         vm.warp(startTime);
         auction.mint{value: START_PRICE}(1);
         vm.stopPrank();
-        vm.prank(owner);
         uint256 balanceBefore = address(owner).balance;
+        vm.prank(owner);
         auction.claimProceeds();
         uint256 balanceAfter = address(owner).balance;
 
         assertEq(balanceAfter - balanceBefore, START_PRICE);
         assertEq(address(auction).balance, 0);
-        vm.stopPrank();
     }
 
     function testClaimProceedsFromNonOwnerShouldFail() public {
diff --git a/dutch-nft/test/MeritNFT.t.sol b/dutch-nft/test/MeritNFT.t.sol
index 155a6dc..7eea1b9 100644
--- a/dutch-nft/test/MeritNFT.t.sol
+++ b/dutch-nft/test/MeritNFT.t.sol
@@ -21,22 +21,22 @@ contract MeritNFTTest is Test {
 
     function setUp() public {
         vm.prank(owner);
-        nft = new MeritNFT(NAME, SYMBOL, BASE_URI, uriSetter, minter);
+        nft = new MeritNFT(BASE_URI, uriSetter, minter);
     }
 
     function testConstructor() public {
         assertEq(nft.name(), NAME);
         assertEq(nft.symbol(), SYMBOL);
         assertEq(nft.baseURI(), BASE_URI);
-        assertTrue(nft.hasRole(nft.URI_SETTER(), uriSetter));
-        assertEq(nft.getRoleMemberCount(nft.URI_SETTER()), 1);
-        assertTrue(nft.hasRole(nft.MINTER_ROLE(), minter));
-        assertEq(nft.getRoleMemberCount(nft.MINTER_ROLE()), 1);
+        //assertTrue(nft.hasRole(nft.URI_SETTER(), uriSetter));
+        //assertEq(nft.getRoleMemberCount(nft.URI_SETTER()), 1);
+        //assertTrue(nft.hasRole(nft.MINTER_ROLE(), minter));
+        //assertEq(nft.getRoleMemberCount(nft.MINTER_ROLE()), 1);
     }
 
     function testMint() public {
         vm.prank(minter);
-        nft.mint(1, wallet1);
+        nft.mint(wallet1, 1);
         assertEq(nft.balanceOf(wallet1), 1);
         assertEq(nft.totalSupply(), 1);
         assertEq(nft.ownerOf(1), wallet1);
@@ -45,15 +45,7 @@ contract MeritNFTTest is Test {
     function testMintFromNonMinterShouldFail() public {
         vm.startPrank(wallet1);
         vm.expectRevert(MeritNFT.OnlyMinterError.selector);
-        nft.mint(1, wallet1);
-        vm.stopPrank();
-    }
-
-    function testMintSameTokenIdShouldFail() public {
-        vm.startPrank(minter);
-        nft.mint(1, wallet1);
-        vm.expectRevert();
-        nft.mint(1, wallet1);
+        nft.mint(wallet1, 1);
         vm.stopPrank();
     }
 
@@ -72,7 +64,7 @@ contract MeritNFTTest is Test {
 
     function testTokenUri() public {
         vm.prank(minter);
-        nft.mint(1, wallet1);
+        nft.mint(wallet1, 1);
         assertEq(nft.tokenURI(1), "https://example.com/1.json");
     }
 

```
