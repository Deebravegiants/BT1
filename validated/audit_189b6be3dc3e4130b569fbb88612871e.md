### Title
Non-refunded Excess ETH in `updateRate` Function - (File: contracts/cross-chain/MultiChainRateProvider.sol)

### Summary
The `updateRate()` function in `MultiChainRateProvider` is `payable` and accepts ETH from any caller to cover LayerZero cross-chain messaging fees. However, it only forwards exactly `estimatedFee` per receiver to the LayerZero endpoint, leaving any excess `msg.value` permanently locked in the contract with no recovery mechanism.

### Finding Description
`MultiChainRateProvider.updateRate()` iterates over all configured rate receivers and, for each, calls `estimateFees()` to obtain the exact LayerZero fee, then sends precisely that amount to the endpoint:

```solidity
(uint256 estimatedFee,) = ILayerZeroEndpoint(layerZeroEndpoint)
    .estimateFees(dstChainId, address(this), _payload, false, bytes(""));

ILayerZeroEndpoint(layerZeroEndpoint).send{ value: estimatedFee }(
    dstChainId, remoteAndLocalAddresses, _payload, payable(msg.sender), address(0x0), bytes("")
);
```

The contract sends exactly `estimatedFee` (not `msg.value`) to LayerZero for each receiver. The LayerZero endpoint's `send` call does include `payable(msg.sender)` as the refund address, but since the contract only forwards `estimatedFee` — not `msg.value` — LayerZero has no surplus to refund. The difference `msg.value − Σ(estimatedFee_i)` remains in the `MultiChainRateProvider` contract.

The contract contains no ETH withdrawal function, so any excess ETH is permanently irrecoverable.

Contrast this with `CrossChainRateProvider.updateRate()`, which correctly forwards the entire `msg.value` to LayerZero and relies on the LayerZero refund mechanism:

```solidity
ILayerZeroEndpoint(layerZeroEndpoint).send{ value: msg.value }(
    dstChainId, remoteAndLocalAddresses, _payload, payable(msg.sender), address(0x0), bytes("")
);
```

`MultiChainRateProvider` does not do this, creating the discrepancy.

### Impact Explanation
Any ETH sent in excess of the exact sum of per-receiver LayerZero fees is permanently frozen inside `MultiChainRateProvider`. Because the contract has no ETH sweep or rescue function, the excess is unrecoverable. This constitutes **permanent freezing of funds** for every caller who overpays — a common and expected pattern when callers buffer against fee fluctuations.

### Likelihood Explanation
`updateRate()` has no access control and is callable by any external account. Callers must estimate the total fee off-chain (summing `estimateFees` across all receivers) and send exactly that amount. Any rounding, stale estimate, or deliberate buffer results in locked ETH. The number of receivers can change over time (via `addRateReceiver`/`removeRateReceiver`), making exact off-chain estimation error-prone.

### Recommendation
After the loop, refund any remaining ETH balance to `msg.sender`:

```solidity
function updateRate() external payable nonReentrant {
    // ... existing loop ...

    // Refund excess ETH to caller
    uint256 remaining = address(this).balance;
    if (remaining > 0) {
        (bool success,) = payable(msg.sender).call{ value: remaining }("");
        require(success, "ETH refund failed");
    }

    emit RateUpdated(rate);
}
```

### Proof of Concept
1. `MultiChainRateProvider` is configured with 3 rate receivers.
2. Caller calls `updateRate()` with `msg.value = 0.03 ether` to ensure coverage.
3. `estimateFees()` returns `0.008 ether` for each of the 3 receivers → total consumed = `0.024 ether`.
4. After the loop, `0.006 ether` remains in the contract.
5. No function exists to withdraw it; the `0.006 ether` is permanently locked.
6. The caller's balance is reduced by `0.03 ether` instead of `0.024 ether`, with no recourse. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

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
