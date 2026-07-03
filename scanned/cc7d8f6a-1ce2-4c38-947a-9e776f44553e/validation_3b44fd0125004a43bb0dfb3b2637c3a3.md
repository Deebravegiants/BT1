### Title
Excess ETH Permanently Locked in `MultiChainRateProvider` Due to Missing `msg.value` Equality Check - (File: contracts/cross-chain/MultiChainRateProvider.sol)

---

### Summary

The `updateRate()` function in `MultiChainRateProvider` (inherited by `RSETHMultiChainRateProvider`) is publicly callable and `payable`. It loops over all configured `rateReceivers`, spending a per-receiver `estimatedFee` from `msg.value` for each LayerZero send. There is no check that `msg.value` equals the sum of all fees consumed, and no refund path exists. Any ETH sent above the total consumed fees is permanently locked in the contract.

---

### Finding Description

`MultiChainRateProvider.updateRate()` is an unrestricted `external payable` function:

```solidity
function updateRate() external payable nonReentrant {
    ...
    for (uint256 i; i < rateReceiversLength;) {
        ...
        (uint256 estimatedFee,) = ILayerZeroEndpoint(layerZeroEndpoint)
            .estimateFees(dstChainId, address(this), _payload, false, bytes(""));

        ILayerZeroEndpoint(layerZeroEndpoint).send{ value: estimatedFee }(
            dstChainId, remoteAndLocalAddresses, _payload, payable(msg.sender), address(0x0), bytes("")
        );
        ...
    }
}
``` [1](#0-0) 

The function forwards exactly `estimatedFee` per receiver to the LayerZero endpoint. However:

1. There is no `require(msg.value == totalEstimatedFee)` guard before the loop.
2. There is no post-loop refund of `msg.value - totalConsumed` to `msg.sender`.
3. The contract inherits only `Ownable` and `ReentrancyGuard` — it contains no ETH withdrawal or recovery function. [2](#0-1) 

The concrete deployed contract `RSETHMultiChainRateProvider` inherits this behavior directly without adding any override or guard. [3](#0-2) 

Compare this to every other bridge function in the codebase (e.g., `RSETHPool.bridgeAssets`, `L1Vault.bridgeRsETHToL2`, `TACWETHBridge.bridgeTokenToL1`) which all enforce `if (msg.value != nativeFee) revert`. The `updateRate()` function is the sole payable entry point that omits this check. [4](#0-3) 

---

### Impact Explanation

Any ETH sent in excess of the sum of per-receiver `estimatedFee` values is irrecoverably locked in `MultiChainRateProvider` / `RSETHMultiChainRateProvider`. The contract has no `receive()` fallback, no `withdraw()`, and no sweep function. The excess ETH cannot be retrieved by any party — **permanent freezing of funds**.

---

### Likelihood Explanation

`updateRate()` carries no access control — any externally owned account or contract can call it. Callers must estimate the correct total fee off-chain (by summing `estimateFees()` across all receivers). The number of receivers can change over time as the owner adds or removes entries, making the correct total non-trivial to compute atomically. A caller who over-estimates (a common defensive pattern) or whose off-chain estimate is stale will permanently lose the excess ETH. The function is also callable by keeper bots or integrators who may not implement exact-fee logic.

---

### Recommendation

Add a pre-loop accumulation and equality check, mirroring the fix applied in the reference report:

```solidity
function updateRate() external payable nonReentrant {
    uint256 latestRate = getLatestRate();
    rate = latestRate;
    lastUpdated = block.timestamp;

    bytes memory _payload = abi.encode(latestRate);
    uint256 rateReceiversLength = rateReceivers.length;

    // Compute total fee first
    uint256 totalFee = 0;
    for (uint256 i; i < rateReceiversLength;) {
        uint16 dstChainId = uint16(rateReceivers[i]._chainId);
        (uint256 estimatedFee,) = ILayerZeroEndpoint(layerZeroEndpoint)
            .estimateFees(dstChainId, address(this), _payload, false, bytes(""));
        totalFee += estimatedFee;
        unchecked { ++i; }
    }
    require(msg.value == totalFee, "Incorrect ETH amount sent");

    // Then relay
    for (uint256 i; i < rateReceiversLength;) {
        // ... existing send logic ...
    }
    emit RateUpdated(rate);
}
```

Alternatively, refund `msg.value - totalConsumed` to `msg.sender` after the loop.

---

### Proof of Concept

1. Owner configures two `rateReceivers` on `RSETHMultiChainRateProvider`.
2. Off-chain, a caller queries `estimateTotalFee()` which returns `0.01 ETH`.
3. Caller calls `updateRate{ value: 0.02 ETH }()` (over-estimating for safety).
4. The loop consumes exactly `0.01 ETH` across the two LayerZero sends.
5. The remaining `0.01 ETH` sits in the contract with no withdrawal path.
6. Caller's `0.01 ETH` is permanently locked. [5](#0-4) [6](#0-5)

### Citations

**File:** contracts/cross-chain/MultiChainRateProvider.sol (L13-13)
```text
abstract contract MultiChainRateProvider is Ownable, ReentrancyGuard {
```

**File:** contracts/cross-chain/MultiChainRateProvider.sol (L108-134)
```text
    function updateRate() external payable nonReentrant {
        uint256 latestRate = getLatestRate();

        rate = latestRate;

        lastUpdated = block.timestamp;

        bytes memory _payload = abi.encode(latestRate);

        uint256 rateReceiversLength = rateReceivers.length;

        for (uint256 i; i < rateReceiversLength;) {
            uint16 dstChainId = uint16(rateReceivers[i]._chainId);

            bytes memory remoteAndLocalAddresses = abi.encodePacked(rateReceivers[i]._contract, address(this));

            (uint256 estimatedFee,) = ILayerZeroEndpoint(layerZeroEndpoint)
                .estimateFees(dstChainId, address(this), _payload, false, bytes(""));

            ILayerZeroEndpoint(layerZeroEndpoint).send{ value: estimatedFee }(
                dstChainId, remoteAndLocalAddresses, _payload, payable(msg.sender), address(0x0), bytes("")
            );

            unchecked {
                ++i;
            }
        }
```

**File:** contracts/cross-chain/MultiChainRateProvider.sol (L154-173)
```text
    function estimateTotalFee() external view returns (uint256 totalEstimatedFee) {
        uint256 latestRate = getLatestRate();

        bytes memory _payload = abi.encode(latestRate);

        uint256 rateReceiversLength = rateReceivers.length;

        for (uint256 i; i < rateReceiversLength;) {
            uint16 dstChainId = uint16(rateReceivers[i]._chainId);

            (uint256 estimatedFee,) = ILayerZeroEndpoint(layerZeroEndpoint)
                .estimateFees(dstChainId, address(this), _payload, false, bytes(""));

            totalEstimatedFee += estimatedFee;

            unchecked {
                ++i;
            }
        }
    }
```

**File:** contracts/cross-chain/RSETHMultiChainRateProvider.sol (L9-9)
```text
contract RSETHMultiChainRateProvider is MultiChainRateProvider {
```

**File:** contracts/L1Vault.sol (L236-238)
```text
        if (msg.value != nativeFee) {
            revert IncorrectNativeFee();
        }
```
