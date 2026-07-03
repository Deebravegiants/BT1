### Title
Unbounded `rateReceivers` array causes `updateRate()` to exceed block gas limit — (`contracts/cross-chain/MultiChainRateProvider.sol`)

### Summary

`addRateReceiver()` imposes no cap on the `rateReceivers` array. `updateRate()` is a public, permissionless function that iterates over every receiver and issues a LayerZero `send` per iteration. As the array grows, gas consumption grows linearly and can permanently exceed the block gas limit, making cross-chain rate propagation impossible.

### Finding Description

`addRateReceiver()` unconditionally pushes to `rateReceivers` with no length check: [1](#0-0) 

`updateRate()` is `external payable` with no access control, and loops over every receiver, calling `estimateFees` and `send` for each: [2](#0-1) 

Each iteration of the loop at line 119 performs two external calls to the LayerZero endpoint — `estimateFees` and `send` — both of which are non-trivial in gas cost. [3](#0-2) 

`AGETHMultiChainRateProvider` inherits this directly without adding any cap: [4](#0-3) 

### Impact Explanation

Once `rateReceivers.length` grows large enough that the cumulative gas of N `estimateFees` + N `send` calls exceeds the block gas limit (~30M on Ethereum mainnet), **no caller — including the owner — can successfully execute `updateRate()`**. Cross-chain agETH rate propagation is permanently frozen. This matches the allowed impact: **Medium — Unbounded gas consumption**.

### Likelihood Explanation

The owner controls `addRateReceiver()`, so this is not an external attacker scenario. However:
- The owner has no on-chain guard preventing over-addition.
- As the protocol expands to more chains, receivers accumulate organically.
- Even at moderate scale (e.g., 30–50 chains, each with expensive LZ `send` calls), the transaction can become prohibitively expensive or revert OOG.
- There is no `removeRateReceiver` path that is guaranteed to be exercised before the limit is hit.

The likelihood is **medium** — it does not require malicious intent, only organic protocol growth without a cap.

### Recommendation

1. Enforce a maximum receiver count in `addRateReceiver()`:
   ```solidity
   uint256 public constant MAX_RATE_RECEIVERS = 20;
   require(rateReceivers.length < MAX_RATE_RECEIVERS, "Too many receivers");
   ```
2. Alternatively, allow `updateRate()` to accept a range `(start, end)` so updates can be batched across multiple transactions.

### Proof of Concept

```solidity
// Foundry test (local mock LZ endpoint)
function test_updateRate_OOG() public {
    for (uint16 i = 0; i < 500; i++) {
        vm.prank(owner);
        provider.addRateReceiver(i, address(receiver));
    }
    // Any caller can trigger the OOG
    vm.deal(address(this), 100 ether);
    vm.expectRevert(); // OOG or gas exhaustion
    provider.updateRate{value: 50 ether}();
}
```

The loop at line 119 of `MultiChainRateProvider.sol` will attempt 500 × (estimateFees + send) external calls, exhausting the block gas limit. [3](#0-2)

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

**File:** contracts/agETH/AGETHMultiChainRateProvider.sol (L12-31)
```text
contract AGETHMultiChainRateProvider is MultiChainRateProvider {
    address public immutable agETHPriceOracle;

    constructor(address _agETHPriceOracle, address _layerZeroEndpoint) {
        agETHPriceOracle = _agETHPriceOracle;

        rateInfo = RateInfo({
            tokenSymbol: "agETH",
            tokenAddress: 0xe1B4d34E8754600962Cd944B535180Bd758E6c2e, // agETH token address on ETH mainnet
            baseTokenSymbol: "ETH",
            baseTokenAddress: address(0) // Address 0 for native tokens
        });

        layerZeroEndpoint = _layerZeroEndpoint;
    }

    /// @notice Returns the latest rate from the agETH rate provider contract
    function getLatestRate() public view override returns (uint256) {
        return IAgEthRateProvider(agETHPriceOracle).getRate();
    }
```
