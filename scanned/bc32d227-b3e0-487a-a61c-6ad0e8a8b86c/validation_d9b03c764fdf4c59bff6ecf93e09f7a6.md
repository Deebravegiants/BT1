### Title
Independent `updateRate()` Calls on Two Separate Providers Allow Cross-Chain Rate Divergence — (`contracts/cross-chain/RSETHRateProvider.sol` / `contracts/cross-chain/RSETHMultiChainRateProvider.sol`)

---

### Summary

The protocol deploys two independent provider contracts — `RSETHRateProvider` (single-chain) and `RSETHMultiChainRateProvider` (multi-chain) — both reading from the same `ILRTOracle.rsETHPrice()`. Because their `updateRate()` functions are permissionless and operate independently, any caller can advance one provider's snapshot without advancing the other, causing receivers on different chains to hold divergent rate snapshots from the same oracle.

---

### Finding Description

`RSETHRateProvider` inherits `CrossChainRateProvider`, which exposes a permissionless `updateRate()`: [1](#0-0) 

`RSETHMultiChainRateProvider` inherits `MultiChainRateProvider`, which exposes its own independent permissionless `updateRate()`: [2](#0-1) 

Both `getLatestRate()` implementations read from the identical oracle storage slot: [3](#0-2) [4](#0-3) 

There is no shared update path, no atomic broadcast, and no on-chain enforcement that both providers must be updated in the same transaction or block. After the oracle advances (e.g., via `updateRSETHPrice()`), an unprivileged caller can invoke `updateRate()` on `RSETHMultiChainRateProvider` only, pushing the new rate to its registered receivers while the `RSETHRateProvider`'s single receiver retains the prior snapshot. The `RSETHRateReceiver` on the destination chain simply stores whatever rate it last received: [5](#0-4) 

---

### Impact Explanation

The invariant that all cross-chain receivers reflect the same rsETH/ETH rate at any given time is broken. Receivers served by `RSETHRateProvider` (e.g., Polygon zkEVM) can hold a stale rate while receivers served by `RSETHMultiChainRateProvider` (e.g., Arbitrum) hold the current rate. Any downstream protocol consuming the stale rate will misprice rsETH relative to ETH, causing users on the stale chain to receive incorrect amounts. This matches **Low — Contract fails to deliver promised returns, but doesn't lose value**.

---

### Likelihood Explanation

The divergence requires no privilege — `updateRate()` on both contracts is fully permissionless. It arises naturally any time the two providers are not updated atomically, which is the normal operational case given they are separate contracts with no coordination mechanism. The window persists until someone calls `updateRate()` on the lagging provider.

---

### Recommendation

Consolidate rate broadcasting into a single contract (i.e., retire `RSETHRateProvider` and migrate its receiver into `RSETHMultiChainRateProvider`'s `rateReceivers` array). This ensures a single `updateRate()` call atomically pushes the same snapshot to all chains. If both contracts must coexist, add an `onlyOwner` or `onlyKeeper` guard to `updateRate()` and enforce that both are called in the same keeper transaction.

---

### Proof of Concept

```solidity
// 1. Oracle advances
lrtOracle.updateRSETHPrice(); // rsETHPrice increases from X to Y

// 2. Caller updates only the MultiChain provider
multiChainProvider.updateRate{value: fee}();
// → RSETHRateReceiver on Arbitrum now holds rate Y

// 3. RSETHRateProvider is NOT updated
// → RSETHRateReceiver on Polygon zkEVM still holds rate X

// 4. Assert divergence
assert(polygonReceiver.rate() != arbitrumReceiver.rate()); // X != Y
// Both receivers read from the same oracle, but hold different snapshots
```

The divergence is directly observable on-chain: `RSETHRateProvider.rate` [6](#0-5)  will differ from `RSETHMultiChainRateProvider.rate` [7](#0-6)  after a selective `updateRate()` call, with no admin action required.

### Citations

**File:** contracts/cross-chain/CrossChainRateProvider.sol (L13-14)
```text
    /// @notice Last rate updated on the provider
    uint256 public rate;
```

**File:** contracts/cross-chain/CrossChainRateProvider.sol (L85-101)
```text
    function updateRate() external payable nonReentrant {
        uint256 latestRate = getLatestRate();

        bytes memory remoteAndLocalAddresses = abi.encodePacked(rateReceiver, address(this));

        rate = latestRate;

        lastUpdated = block.timestamp;

        bytes memory _payload = abi.encode(latestRate);

        ILayerZeroEndpoint(layerZeroEndpoint).send{ value: msg.value }(
            dstChainId, remoteAndLocalAddresses, _payload, payable(msg.sender), address(0x0), bytes("")
        );

        emit RateUpdated(rate);
    }
```

**File:** contracts/cross-chain/MultiChainRateProvider.sol (L13-14)
```text
abstract contract MultiChainRateProvider is Ownable, ReentrancyGuard {
    /// @notice Last rate updated on the provider
```

**File:** contracts/cross-chain/MultiChainRateProvider.sol (L108-137)
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

        emit RateUpdated(rate);
    }
```

**File:** contracts/cross-chain/RSETHRateProvider.sol (L27-29)
```text
    function getLatestRate() public view override returns (uint256) {
        return ILRTOracle(rsETHPriceOracle).rsETHPrice();
    }
```

**File:** contracts/cross-chain/RSETHMultiChainRateProvider.sol (L26-28)
```text
    function getLatestRate() public view override returns (uint256) {
        return ILRTOracle(rsETHPriceOracle).rsETHPrice();
    }
```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L82-99)
```text
    function lzReceive(uint16 _srcChainId, bytes memory _srcAddress, uint64, bytes calldata _payload) external {
        require(msg.sender == layerZeroEndpoint, "Sender should be lz endpoint");

        address srcAddress;
        assembly {
            srcAddress := mload(add(_srcAddress, 20))
        }

        require(_srcChainId == srcChainId, "Src chainId must be correct");
        require(srcAddress == rateProvider, "Src address must be provider");

        uint256 _rate = abi.decode(_payload, (uint256));

        rate = _rate;

        lastUpdated = block.timestamp;

        emit RateUpdated(_rate);
```
