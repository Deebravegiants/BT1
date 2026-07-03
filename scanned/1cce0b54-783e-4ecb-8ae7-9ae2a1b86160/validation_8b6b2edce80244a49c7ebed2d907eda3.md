### Title
Unbounded Loop in `updateRate()` Over Growing `rateReceivers` Array Can Exceed Block Gas Limit - (File: contracts/cross-chain/MultiChainRateProvider.sol)

### Summary
`MultiChainRateProvider.updateRate()` iterates over every entry in the `rateReceivers` array and issues a LayerZero `send()` call for each one. There is no cap on how many receivers can be registered. As the protocol deploys to additional L2 chains, the array grows and the gas cost of a single `updateRate()` call grows proportionally. Once the cumulative cost exceeds the block gas limit the function becomes permanently uncallable, freezing cross-chain rate propagation.

### Finding Description
`updateRate()` is an unrestricted `external payable` function. Its core body is:

```solidity
for (uint256 i; i < rateReceiversLength;) {
    uint16 dstChainId = uint16(rateReceivers[i]._chainId);
    bytes memory remoteAndLocalAddresses = abi.encodePacked(rateReceivers[i]._contract, address(this));
    (uint256 estimatedFee,) = ILayerZeroEndpoint(layerZeroEndpoint)
        .estimateFees(dstChainId, address(this), _payload, false, bytes(""));
    ILayerZeroEndpoint(layerZeroEndpoint).send{ value: estimatedFee }(
        dstChainId, remoteAndLocalAddresses, _payload, payable(msg.sender), address(0x0), bytes("")
    );
    unchecked { ++i; }
}
``` [1](#0-0) 

Each iteration performs two external calls (`estimateFees` + `send`) against the LayerZero endpoint. Both are non-trivial in gas cost. The `rateReceivers` array is grown by the owner via `addRateReceiver()` with no maximum length enforced:

```solidity
function addRateReceiver(uint16 _chainId, address _contract) external onlyOwner {
    rateReceivers.push(RateReceiver({ _chainId: _chainId, _contract: _contract }));
    ...
}
``` [2](#0-1) 

There is no batch mechanism and no length cap. `updateRate()` itself carries no access control: [3](#0-2) 

### Impact Explanation
When the cumulative gas of all `estimateFees` + `send` calls exceeds the block gas limit (~30 M gas on Ethereum), every invocation of `updateRate()` reverts. The rsETH/ETH exchange rate can no longer be pushed to any L2 receiver contract. L2 pools that depend on this rate for minting/redeeming rsETH will operate on a permanently stale price, breaking the cross-chain rate propagation mechanism. This constitutes **Medium – unbounded gas consumption** leading to **temporary (potentially permanent) freezing of rate updates** and incorrect rsETH accounting on L2.

### Likelihood Explanation
The Kelp DAO protocol is actively expanding to new L2 networks (Arbitrum, Optimism, Unichain, and others are already referenced in the codebase). Each new deployment adds one entry to `rateReceivers`. A LayerZero `send()` call costs on the order of 50 000–150 000 gas depending on the destination chain configuration. With Ethereum's ~30 M block gas limit, the function becomes uncallable somewhere in the range of 200–600 registered receivers. While that number is not reached today, the trajectory is clear and no architectural guard prevents it.

### Recommendation
1. **Batch updates**: Split `updateRate()` into a paginated variant that accepts a start index and count, allowing callers to push the rate to a subset of receivers per transaction.
2. **Enforce a maximum length**: Add a `maxRateReceivers` constant and revert in `addRateReceiver()` when the limit would be exceeded.
3. **Per-chain update**: Expose a `updateRateForChain(uint256 index)` function so individual receivers can be updated independently.

### Proof of Concept
1. Owner calls `addRateReceiver()` N times (one per supported L2 chain) until `rateReceivers.length` is large enough that the cumulative gas of N × (`estimateFees` + `send`) exceeds the block gas limit.
2. Any caller (including the protocol's own keeper) calls `updateRate()`.
3. The transaction reverts with an out-of-gas error.
4. All L2 receiver contracts are now stuck with the last successfully propagated rate; no further rate updates are possible through this path. [3](#0-2)

### Citations

**File:** contracts/cross-chain/MultiChainRateProvider.sol (L72-76)
```text
    function addRateReceiver(uint16 _chainId, address _contract) external onlyOwner {
        rateReceivers.push(RateReceiver({ _chainId: _chainId, _contract: _contract }));

        emit RateReceiverAdded(_chainId, _contract);
    }
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
