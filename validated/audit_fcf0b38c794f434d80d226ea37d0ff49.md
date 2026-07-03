### Title
Insufficient `msg.value` Validation in Batch LayerZero Send Loop Causes Rate Update Failure - (File: contracts/cross-chain/MultiChainRateProvider.sol)

### Summary
`MultiChainRateProvider::updateRate()` loops through all registered `rateReceivers` and calls `ILayerZeroEndpoint.send{ value: estimatedFee }` for each destination chain. There is no validation that `msg.value` is sufficient to cover the sum of all per-chain fees. Additionally, the `refundAddress` is set to `payable(msg.sender)`, meaning any excess ETH from each `send` call is returned to the caller — not back to the contract — making it unavailable for subsequent loop iterations. If `msg.value < sum(all estimatedFees)`, the contract exhausts its ETH balance mid-loop and the entire transaction reverts, failing to propagate the rate to any chain.

### Finding Description
In `MultiChainRateProvider.updateRate()` (lines 108–137), the function iterates over all `rateReceivers`, estimates the per-chain LayerZero fee via `estimateFees`, and immediately calls `send{ value: estimatedFee }` for each chain:

```solidity
for (uint256 i; i < rateReceiversLength;) {
    (uint256 estimatedFee,) = ILayerZeroEndpoint(layerZeroEndpoint)
        .estimateFees(dstChainId, address(this), _payload, false, bytes(""));

    ILayerZeroEndpoint(layerZeroEndpoint).send{ value: estimatedFee }(
        dstChainId, remoteAndLocalAddresses, _payload, payable(msg.sender), address(0x0), bytes("")
    );
    unchecked { ++i; }
}
```

Each `send` call deducts `estimatedFee` from the contract's ETH balance. Any excess is refunded to `payable(msg.sender)` — not back to the contract — so it cannot fund subsequent iterations. There is no pre-loop check that `msg.value >= sum(estimatedFee_i for all i)`. If the caller underpays, the contract runs out of ETH partway through the loop and the transaction reverts entirely.

The helper `estimateTotalFee()` exists (lines 154–173) but is never enforced inside `updateRate()`. The concrete implementations `RSETHMultiChainRateProvider` and `AGETHMultiChainRateProvider` both inherit this unfixed base.

### Impact Explanation
When `updateRate()` reverts, the rsETH/agETH exchange rate is not propagated to any destination chain. The on-chain `rate` and `lastUpdated` state variables are also rolled back (since the revert undoes all state changes). Destination-chain receiver contracts retain their previously stored stale rate. Any protocol component on those chains that reads the rate (e.g., for pricing or accounting) will operate on an outdated value until a successful `updateRate()` call is made. No ETH is permanently lost, but the contract fails to deliver its core promised function.

**Impact: Low — Contract fails to deliver promised returns, but doesn't lose value.**

### Likelihood Explanation
`updateRate()` is `external` and callable by any unprivileged address. The function provides no on-chain guidance about the required ETH amount. A caller who does not first call `estimateTotalFee()` off-chain — or who calls `updateRate()` when fees have risen since their estimate — will trigger the revert. As the number of registered `rateReceivers` grows, the probability of underpayment increases. This is a realistic operational failure path.

### Recommendation
Add a pre-loop validation requiring `msg.value` to cover the total estimated fee across all receivers:

```solidity
uint256 totalFee;
for (uint256 i; i < rateReceiversLength; ++i) {
    (uint256 fee,) = ILayerZeroEndpoint(layerZeroEndpoint)
        .estimateFees(uint16(rateReceivers[i]._chainId), address(this), _payload, false, bytes(""));
    totalFee += fee;
}
require(msg.value >= totalFee, "Insufficient fee");
```

Alternatively, change the `refundAddress` from `payable(msg.sender)` to `payable(address(this))` so that excess ETH from each `send` call is returned to the contract and can fund subsequent iterations. Combine with a final sweep to return any remaining ETH to `msg.sender`.

### Proof of Concept

1. Deploy `RSETHMultiChainRateProvider` with two `rateReceivers` on different chains (e.g., Arbitrum and Optimism).
2. Call `estimateTotalFee()` off-chain — suppose it returns `0.002 ETH` (0.001 per chain).
3. Call `updateRate{ value: 0.001 ETH }()` (only enough for one chain).
4. Iteration 0: `estimateFees` returns `0.001 ETH`. `send{ value: 0.001 ETH }` succeeds. Contract balance: `0 ETH`.
5. Iteration 1: `estimateFees` returns `0.001 ETH`. `send{ value: 0.001 ETH }` reverts — contract has no ETH.
6. Entire transaction reverts. Rate is not updated on either chain. `rate` and `lastUpdated` storage remain at their previous values. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

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

**File:** contracts/cross-chain/RSETHMultiChainRateProvider.sol (L9-28)
```text
contract RSETHMultiChainRateProvider is MultiChainRateProvider {
    address public immutable rsETHPriceOracle;

    constructor(address _rsETHPriceOracle, address _layerZeroEndpoint) {
        rsETHPriceOracle = _rsETHPriceOracle;

        rateInfo = RateInfo({
            tokenSymbol: "rsETH",
            tokenAddress: 0xA1290d69c65A6Fe4DF752f95823fae25cB99e5A7, // rsETH token address on ETH mainnet
            baseTokenSymbol: "ETH",
            baseTokenAddress: address(0) // Address 0 for native tokens
        });

        layerZeroEndpoint = _layerZeroEndpoint;
    }

    /// @notice Returns the latest rate from the rsETH contract
    function getLatestRate() public view override returns (uint256) {
        return ILRTOracle(rsETHPriceOracle).rsETHPrice();
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
