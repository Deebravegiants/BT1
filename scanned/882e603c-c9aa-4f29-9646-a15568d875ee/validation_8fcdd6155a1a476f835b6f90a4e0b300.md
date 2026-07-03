### Title
Excess ETH Permanently Stuck in Contract When `updateRate()` Called with Surplus Value - (File: contracts/cross-chain/MultiChainRateProvider.sol)

### Summary
`MultiChainRateProvider.updateRate()` is a public payable function with no access control. It sends exactly the on-chain `estimatedFee` to each LayerZero endpoint call per receiver, but never returns any remaining `msg.value` to the caller. Because the contract has no ETH recovery mechanism, any ETH sent beyond the sum of per-receiver estimated fees is permanently locked.

### Finding Description
`updateRate()` iterates over all configured `rateReceivers`, queries `estimateFees()` for each, and forwards exactly that amount to `ILayerZeroEndpoint.send()`:

```solidity
(uint256 estimatedFee,) = ILayerZeroEndpoint(layerZeroEndpoint)
    .estimateFees(dstChainId, address(this), _payload, false, bytes(""));

ILayerZeroEndpoint(layerZeroEndpoint).send{ value: estimatedFee }(
    dstChainId, remoteAndLocalAddresses, _payload, payable(msg.sender), address(0x0), bytes("")
);
```

The `payable(msg.sender)` argument is LayerZero's internal refund address for its own excess gas, not a mechanism for the contract to return the caller's unspent `msg.value`. After the loop, no refund of the difference `msg.value − Σ(estimatedFee_i)` is issued. The contract is `Ownable` but contains no ETH sweep or rescue function, so any surplus ETH is permanently frozen.

This contrasts with `CrossChainRateProvider.updateRate()`, which correctly forwards the full `msg.value` to the single LayerZero call and lets LayerZero refund the excess:

```solidity
ILayerZeroEndpoint(layerZeroEndpoint).send{ value: msg.value }(
    dstChainId, remoteAndLocalAddresses, _payload, payable(msg.sender), address(0x0), bytes("")
);
```

`MultiChainRateProvider` does not do this because it must split the value across multiple receivers.

### Impact Explanation
Any ETH sent above the exact sum of per-receiver estimated fees is permanently frozen in the `MultiChainRateProvider` contract. There is no owner-callable sweep, no `receive()` drain path, and no upgrade path that would recover it. This constitutes permanent freezing of caller funds.

### Likelihood Explanation
`updateRate()` carries no access control — any external account or contract may call it. LayerZero fees fluctuate with gas prices and oracle state. Callers who use `estimateTotalFee()` off-chain and then add a safety buffer (a standard practice to avoid reverts) will routinely send more ETH than consumed. The gap between estimate and actual fee is small per call but accumulates over time across many callers.

### Recommendation
After the loop, refund any unspent ETH to `msg.sender`:

```solidity
uint256 remaining = address(this).balance;
if (remaining > 0) {
    (bool ok,) = payable(msg.sender).call{value: remaining}("");
    require(ok, "refund failed");
}
```

Alternatively, require `msg.value` to equal the pre-computed total fee exactly, reverting if it does not match.

### Proof of Concept
1. Suppose two rate receivers are configured; `estimateTotalFee()` returns `0.01 ETH`.
2. Caller invokes `updateRate{value: 0.02 ETH}()` — a common pattern to avoid reverts from fee fluctuation.
3. The loop sends `estimatedFee_0` and `estimatedFee_1` (summing to `0.01 ETH`) to LayerZero.
4. After the loop, `address(this).balance == 0.01 ETH`. No refund is issued.
5. The `0.01 ETH` surplus is permanently locked; the contract has no function to recover it. [1](#0-0) [2](#0-1) [3](#0-2)

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

**File:** contracts/cross-chain/CrossChainRateProvider.sol (L85-99)
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

```
