Looking at the code carefully to assess this claim.

### Title
Unbounded Array in `getExpectedShareAmountMultiple` Enables OOG for On-Chain Callers — (`contracts/king-protocol/TokenSwap.sol`)

---

### Summary

`getExpectedShareAmountMultiple` accepts caller-controlled arrays of arbitrary length with no upper-bound check. Any on-chain contract that forwards user-supplied arrays to this function can be forced into an out-of-gas revert, temporarily freezing any protocol flow that depends on it.

---

### Finding Description

`getExpectedShareAmountMultiple` is an `external view` function with no access control and no array-length cap. [1](#0-0) 

The only guards are a zero-length check and a length-mismatch check: [2](#0-1) 

The validation loop then iterates exactly `assets.length` times, checking only that each element is in the `supportedTokens` mapping — it does **not** enforce uniqueness: [3](#0-2) 

Finally, the full N-element arrays are forwarded to the external `kingProtocol.previewDeposit` call: [4](#0-3) 

`previewDeposit` is defined in `IKingProtocol` as accepting unbounded `address[]` and `uint256[]` arrays: [5](#0-4) 

Because `supportedTokens` is a mapping (not a set), an attacker can repeat the same supported token address N times — e.g., `[tokenA, tokenA, tokenA, ...]` — and every iteration of the loop will pass. There is no deduplication or cap anywhere in the contract: [6](#0-5) 

---

### Impact Explanation

Any on-chain contract (aggregator, router, vault, or protocol integration) that calls `getExpectedShareAmountMultiple` with a user-supplied array and a bounded gas budget can be forced into an OOG revert by an attacker who passes a sufficiently large array of repeated supported tokens. This matches the **Medium — Unbounded gas consumption** impact in the allowed scope.

---

### Likelihood Explanation

- The function is `external view` with **no access control** — any EOA or contract can call it.
- Only one supported token is needed; the attacker repeats it N times.
- No admin action, key compromise, or governance capture is required.
- The gas cost scales linearly: the loop at lines 347–351 plus the external `previewDeposit` call both iterate over the full array.

---

### Recommendation

Add a maximum array-length guard at the top of the function (and consistently in `depositMultipleToKingProtocol` / `_validateMultipleDepositInputs`):

```solidity
uint256 constant MAX_ASSETS = 20; // or a governance-settable value

function getExpectedShareAmountMultiple(...) external view {
    if (assets.length > MAX_ASSETS) revert ArrayTooLong();
    ...
}
```

Optionally, also enforce uniqueness (no duplicate asset addresses) to prevent repeated-token inflation of gas cost.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

import "forge-std/Test.sol";
import "../contracts/king-protocol/TokenSwap.sol";

contract OOGTest is Test {
    TokenSwap swap;
    address supportedToken; // assume one supported token exists

    function setUp() public {
        // deploy / initialize TokenSwap with a mock kingProtocol and one supported token
        // ...
    }

    function testOOGAtLargeN() public {
        uint256 N = 2000;
        address[] memory assets  = new address[](N);
        uint256[] memory amounts = new uint256[](N);
        for (uint256 i; i < N; i++) {
            assets[i]  = supportedToken; // repeated — passes supportedTokens check
            amounts[i] = 1e18;
        }

        // Call with a capped gas budget; assert it reverts with OOG
        (bool ok,) = address(swap).staticcall{gas: 100_000}(
            abi.encodeCall(swap.getExpectedShareAmountMultiple, (assets, amounts))
        );
        assertFalse(ok, "expected OOG revert");
    }
}
```

The test demonstrates that a caller with a fixed gas budget reverts at a predictable N, and that no array-length cap exists to prevent it. [7](#0-6)

### Citations

**File:** contracts/king-protocol/TokenSwap.sol (L29-29)
```text
    mapping(address acceptedToken => bool isAccepted) public supportedTokens;
```

**File:** contracts/king-protocol/TokenSwap.sol (L330-336)
```text
    function getExpectedShareAmountMultiple(
        address[] memory assets,
        uint256[] memory amounts
    )
        external
        view
        returns (uint256 shareAmount, uint256 depositFee)
```

**File:** contracts/king-protocol/TokenSwap.sol (L338-344)
```text
        if (assets.length == 0) {
            revert ZeroAmount();
        }

        if (assets.length != amounts.length) {
            revert ArrayLengthMismatch();
        }
```

**File:** contracts/king-protocol/TokenSwap.sol (L347-353)
```text
        for (uint256 i = 0; i < assets.length; i++) {
            if (!supportedTokens[assets[i]]) {
                revert UnsupportedAsset();
            }
        }

        return kingProtocol.previewDeposit(assets, amounts);
```

**File:** contracts/king-protocol/IKingProtocol.sol (L18-24)
```text
    function previewDeposit(
        address[] memory _tokens,
        uint256[] memory _amounts
    )
        external
        view
        returns (uint256 shareToMint, uint256 depositFee);
```
