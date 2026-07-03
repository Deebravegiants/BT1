### Title
Excess ETH Sent to `updateRate()` Is Permanently Trapped With No Refund or Recovery - (File: contracts/cross-chain/MultiChainRateProvider.sol)

### Summary
`MultiChainRateProvider.updateRate()` is a public payable function that accepts `msg.value` to cover LayerZero cross-chain messaging fees. For each registered receiver, it queries `estimateFees()` and forwards only that exact `estimatedFee` to the LayerZero endpoint. Any ETH sent by the caller beyond the sum of all per-receiver estimated fees is silently retained by the contract with no refund path and no owner-accessible recovery function.

### Finding Description
`MultiChainRateProvider.updateRate()` iterates over all `rateReceivers`, estimates the LayerZero fee for each destination chain, and calls `ILayerZeroEndpoint.send{ value: estimatedFee }(...)` with only the per-receiver estimate:

```solidity
// contracts/cross-chain/MultiChainRateProvider.sol lines 108-137
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
    emit RateUpdated(rate);
}
```

The total ETH consumed is `Σ estimatedFee[i]`. If `msg.value > Σ estimatedFee[i]`, the difference is left in the contract. The contract has no `receive()`/`fallback()` ETH withdrawal function, no owner sweep, and no recovery mechanism for native ETH. The excess is permanently frozen.

Contrast this with `CrossChainRateProvider.updateRate()`, which forwards the entire `msg.value` directly to LayerZero and relies on LayerZero's built-in refund mechanism (`payable(msg.sender)` as refund address) to return any excess:

```solidity
// contracts/cross-chain/CrossChainRateProvider.sol line 96
ILayerZeroEndpoint(layerZeroEndpoint).send{ value: msg.value }(
    dstChainId, remoteAndLocalAddresses, _payload, payable(msg.sender), address(0x0), bytes("")
);
```

`MultiChainRateProvider` does not use this pattern; it sends only `estimatedFee` per leg, so LayerZero never receives the excess and cannot refund it.

### Impact Explanation
Any ETH sent to `updateRate()` beyond the sum of per-receiver LayerZero fees is permanently locked in `MultiChainRateProvider` with no recovery path. The contract inherits only `Ownable` and `ReentrancyGuard`; neither provides an ETH sweep function. This constitutes permanent freezing of the excess caller funds.

### Likelihood Explanation
`updateRate()` carries no access control — any external account can call it. Callers must estimate the total fee off-chain before calling; because `estimateFees()` returns a point-in-time estimate that can change between the estimation call and the actual transaction (due to gas price fluctuations or base-fee changes), callers routinely add a buffer. That buffer is the excess that becomes permanently trapped. The more receivers are registered, the larger the potential discrepancy.

### Recommendation
After the loop, refund any unspent ETH to the caller:

```solidity
uint256 remaining = address(this).balance; // or track spent explicitly
if (remaining > 0) {
    (bool ok,) = payable(msg.sender).call{value: remaining}("");
    require(ok, "refund failed");
}
```

Alternatively, adopt the same pattern as `CrossChainRateProvider` and forward `msg.value` directly to LayerZero for each leg (splitting it proportionally), relying on LayerZero's native refund mechanism. At minimum, add an owner-only ETH recovery function.

### Proof of Concept
1. Two receivers are registered in `MultiChainRateProvider`.
2. Off-chain estimation returns `0.001 ETH` per receiver → caller sends `0.003 ETH` as a safety buffer.
3. `updateRate()` calls `estimateFees()` on-chain; both return `0.001 ETH` at execution time.
4. Two `send{ value: 0.001 ETH }` calls consume `0.002 ETH` total.
5. The remaining `0.001 ETH` stays in `MultiChainRateProvider`.
6. No function exists to withdraw it; it is permanently frozen. [1](#0-0) [2](#0-1)

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
