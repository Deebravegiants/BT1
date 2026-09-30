# [?] Merge pull request from GHSA-878m-3g6q-594q

## Summary
Severity: Unknown
Chain: Solidity
Component: OpenZeppelin/openzeppelin-contracts
Published: 2023-03-02
Source: https://github.com/OpenZeppelin/openzeppelin-contracts/commit/8ba26f388f4c1959a071310b4823a7889498e28c
Type: security-commit

## Details
Merge pull request from GHSA-878m-3g6q-594q

* Test batch minting of 1

* Fix balance tracking

* fix lint

* add changeset

* rename UNSAFE -> unsafe

* fix docs

* fix changeset

* grammar

* add explanation of preserved invariant

* add fuzz tests

* rename variable

* improve property definition

* add burn

* add test ownership multiple batches

* refactor fuzz tests

* change ownership test for better probability

* typo

* reorder comment

* update changelog notes

* edit changelog

* lint

* Update CHANGELOG.md

---------

Co-authored-by: Francisco Giordano <fg@frang.io>

### .changeset/brave-olives-laugh.md
```diff
@@ -0,0 +1,5 @@
+---
+'openzeppelin-solidity': patch
+---
+
+`ERC721Consecutive`: Fixed a bug when `_mintConsecutive` is used for batches of size 1 that could lead to balance overflow. Refer to the breaking changes section in the changelog for a note on the behavior of `ERC721._beforeTokenTransfer`.
```

### CHANGELOG.md
```diff
@@ -12,6 +12,10 @@
 - `ERC777`: The `ERC777` token standard is no longer supported by OpenZeppelin. Our implementation is now deprecated and will be removed in the next major release. The corresponding standard interfaces remain available. ([#4066](https://github.com/OpenZeppelin/openzeppelin-contracts/pull/4066))
 - `ERC1820Implementer`: The `ERC1820` pseudo-introspection mechanism is no longer supported by OpenZeppelin. Our implementation is now deprecated and will be removed in the next major release. The corresponding standard interfaces remain available. ([#4066](https://github.com/OpenZeppelin/openzeppelin-contracts/pull/4066))
 
+### Breaking changes
+
+- `ERC721`: The internal function `_beforeTokenTransfer` no longer updates balances, which it previously did when `batchSize` was greater than 1. This change has no consequence unless a custom ERC721 extension is explicitly invoking `_beforeTokenTransfer`. Balance updates in extensions must now be done explicitly using `__unsafe_increaseBalance`, with a name that indicates that there is an invariant that has to be manually verified.
+
 ## 4.8.1 (2023-01-12)
 
 - `ERC4626`: Use staticcall instead of call when fetching underlying ERC-20 decimals. ([#3943](https://github.com/OpenZeppelin/openzeppelin-contracts/pull/3943))
```

### contracts/token/ERC721/ERC721.sol
```diff
@@ -434,21 +434,7 @@ contract ERC721 is Context, ERC165, IERC721, IERC721Metadata {
      *
      * To learn more about hooks, head to xref:ROOT:extending-contracts.adoc#using-hooks[Using Hooks].
      */
-    function _beforeTokenTransfer(
-        address from,
-        address to,
-        uint256 /* firstTokenId */,
-        uint256 batchSize
-    ) internal virtual {
-        if (batchSize > 1) {
-            if (from != address(0)) {
-                _balances[from] -= batchSize;
-            }
-            if (to != address(0)) {
-                _balances[to] += batchSize;
-            }
-        }
-    }
+    function _beforeTokenTransfer(address from, address to, uint256 firstTokenId, uint256 batchSize) internal virtual {}
 
     /**
      * @dev Hook that is called after any token transfer. This includes minting and burning. If {ERC721Consecutive} is
@@ -465,4 +451,16 @@ contract ERC721 is Context, ERC165, IERC721, IERC721Metadata {
      * To learn more about hooks, head to xref:ROOT:extending-contracts.adoc#using-hooks[Using Hooks].
      */
     function _afterTokenTransfer(address from, address to, uint256 firstTokenId, uint256 batchSize) internal virtual {}
+
+    /**
+     * @dev Unsafe write access to the balances, used by extensions that "mint" tokens using an {ownerOf} override.
+     *
+     * WARNING: Anyone calling this MUST ensure that the balances remain consistent with the ownership. The invariant
+     * being that for any address `a` the value returned by `balanceOf(a)` must be equal to the number of tokens such
+     * that `ownerOf(tokenId)` is `a`.
+     */
+    // solhint-disable-next-line func-name-mixedcase
+    function __unsafe_increaseBalance(address account, uint256 amount) internal {
+        _balances[account] += amount;
+    }
 }
```

### contracts/token/ERC721/extensions/ERC721Consecutive.sol
```diff
@@ -96,6 +96,11 @@ abstract contract ERC721Consecutive is IERC2309, ERC721 {
             // push an ownership checkpoint & emit event
             uint96 last = first + batchSize - 1;
             _sequentialOwnership.push(last, uint160(to));
+
+            // The invariant required by this function is preserved because the new sequentialOwnership checkpoint
+            // is attributing ownership of `batchSize` new tokens to account `to`.
+            __unsafe_increaseBalance(to, batchSize);
+
             emit ConsecutiveTransfer(first, last, address(0), to);
 
             // hook after
```

### test/token/ERC721/extensions/ERC721Consecutive.t.sol
```diff
@@ -0,0 +1,120 @@
+// SPDX-License-Identifier: MIT
+
+pragma solidity ^0.8.0;
+
+import "../../../../contracts/token/ERC721/extensions/ERC721Consecutive.sol";
+import "forge-std/Test.sol";
+
+function toSingleton(address account) pure returns (address[] memory) {
+    address[] memory accounts = new address[](1);
+    accounts[0] = account;
+    return accounts;
+}
+
+contract ERC721ConsecutiveTarget is StdUtils, ERC721Consecutive {
+    uint256 public totalMinted = 0;
+
+    constructor(address[] memory receivers, uint256[] memory batches) ERC721("", "") {
+        for (uint256 i = 0; i < batches.length; i++) {
+            address receiver = receivers[i % receivers.length];
+            uint96 batchSize = uint96(bound(batches[i], 0, _maxBatchSize()));
+            _mintConsecutive(receiver, batchSize);
+            totalMinted += batchSize;
+        }
+    }
+
+    function burn(uint256 tokenId) public {
+        _burn(tokenId);
+    }
+}
+
+contract ERC721ConsecutiveTest is Test {
+    function test_balance(address receiver, uint256[] calldata batches) public {
+        vm.assume(receiver != address(0));
+
+        ERC721ConsecutiveTarget token = new ERC721ConsecutiveTarget(toSingleton(receiver), batches);
+
+        assertEq(token.balanceOf(receiver), token.totalMinted());
+    }
+
+    function test_ownership(address receiver, uint256[] calldata batches, uint256[2] calldata unboundedTokenId) public {
+        vm.assume(receiver != address(0));
+
+        ERC721ConsecutiveTarget token = new ERC721ConsecutiveTarget(toSingleton(receiver), batches);
+
+        if (token.totalMinted() > 0) {
+            uint256 validTokenId = bound(unboundedTokenId[0], 0, token.totalMinted() - 1);
+            assertEq(token.ownerOf(validTokenId), receiver);
+        }
+
+        uint256 invalidTokenId = bound(unboundedTokenId[1], token.totalMinted(), type(uint256).max);
+        vm.expectRevert();
+        token.ownerOf(invalidTokenId);
+    }
+
+    function test_burn(address receiver, uint256[] calldata batches, uint256 unboundedTokenId) public {
+        vm.assume(receiver != address(0));
+
+        ERC721ConsecutiveTarget token = new ERC721ConsecutiveTarget(toSingleton(receiver), batches);
+
+        // only test if we minted at least one token
+        uint256 supply = token.totalMinted();
+        vm.assume(supply > 0);
+
+        // burn a token in [0; supply[
+        uint256 tokenId = bound(unboundedTokenId, 0, supply - 1);
+        token.burn(tokenId);
+
+        // balance should have decreased
+        assertEq(token.balanceOf(receiver), supply - 1);
+
+        // token should be burnt
+        vm.expectRevert();
+        token.ownerOf(tokenId);
+    }
+
+    function test_transfer(
+        address[2] calldata accounts,
+        uint256[2] calldata unboundedBatches,
+        uint256[2] calldata unboundedTokenId
+    ) public {
+        vm.assume(accounts[0] != address(0));
+        vm.assume(accounts[1] != address(0));
+        vm.assume(accounts[0] != accounts[1]);
+
+        address[] memory receivers = new address[](2);
+        receivers[0] = accounts[0];
+        receivers[1] = accounts[1];
+
+        // We assume _maxBatchSize is 5000 (the default). This test will break otherwise.
+        uint256[] memory batches = new uint256[](2);
+        batches[0] = bound(unboundedBatches[0], 1, 5000);
+        batches[1] = bound(unboundedBatches[1], 1, 5000);
+
+        ERC721ConsecutiveTarget token = new ERC721ConsecutiveTarget(receivers, batches);
+
+        uint256 tokenId0 = bound(unboundedTokenId[0], 0, batches[0] - 1);
+        uint256 tokenId1 = bound(unboundedTokenId[1], 0, batches[1] - 1) + batches[0];
+
+        assertEq(token.ownerOf(tokenId0), accounts[0]);
+        assertEq(token.ownerOf(tokenId1), accounts[1]);
+        assertEq(token.balanceOf(accounts[0]), batches[0]);
+        assertEq(token.balanceOf(accounts[1]), batches[1]);
+
+        vm.prank(accounts[0]);
+        token.transferFrom(accounts[0], accounts[1], tokenId0);
+
+        assertEq(token.ownerOf(tokenId0), accounts[1]);
+        assertEq(token.ownerOf(tokenId1), accounts[1]);
+        assertEq(token.balanceOf(accounts[0]), batches[0] - 1);
+        assertEq(token.balanceOf(accounts[1]), batches[1] + 1);
+
+        vm.prank(accounts[1]);
+        token.transferFrom(accounts[1], accounts[0], tokenId1);
+
+        assertEq(token.ownerOf(tokenId0), accounts[1]);
+        assertEq(token.ownerOf(tokenId1), accounts[0]);
+        assertEq(token.balanceOf(accounts[0]), batches[0]);
+        assertEq(token.balanceOf(accounts[1]), batches[1]);
+    }
+}
```

### test/token/ERC721/extensions/ERC721Consecutive.test.js
```diff
@@ -12,7 +12,8 @@ contract('ERC721Consecutive', function (accounts) {
   const symbol = 'NFT';
   const batches = [
     { receiver: user1, amount: 0 },
-    { receiver: user1, amount: 3 },
+    { receiver: user1, amount: 1 },
+    { receiver: user1, amount: 2 },
     { receiver: user2, amount: 5 },
     { receiver: user3, amount: 0 },
     { receiver: user1, amount: 7 },
```
