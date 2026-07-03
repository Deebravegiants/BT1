### Title
Excess ETH Permanently Locked in `MultiChainRateProvider` Due to No Refund Mechanism - (File: contracts/cross-chain/MultiChainRateProvider.sol)

### Summary
`MultiChainRateProvider.updateRate()` is a `payable` function that iterates over all registered rate receivers and sends exactly `estimatedFee` to each LayerZero endpoint call. Any ETH sent by the caller beyond the sum of all estimated fees is permanently trapped in the contract, as there is no `receive()` fallback, no sweep function, and no ETH recovery path.

### Finding Description
`updateRate()` is marked `payable` and is callable by any external account with no access control. Inside the loop, it calls `estimateFees()` on-chain to compute the fee for each destination chain, then calls `send{ value: estimatedFee }(...)`. The refund address passed to LayerZero is `payable(msg.sender)`, so LayerZero refunds any unused gas back to the caller — but only for the portion it received. Any ETH that was included in `msg.value` but never forwarded to LayerZero (i.e., `msg.value - Σ estimatedFee`) stays in the `MultiChainRateProvider` contract itself.

The abstract contract declares no `receive()` function, no `fallback()`, and no owner-callable ETH sweep. Concrete implementations that do not add such a mechanism inherit this gap. [1](#0-0) 

The critical lines:

```solidity
function updateRate() external payable nonReentrant {
    ...
    for (uint256 i; i < rateReceiversLength;) {
        (uint256 estimatedFee,) = ILayerZeroEndpoint(layerZeroEndpoint)
            .estimateFees(dstChainId, address(this), _payload, false, bytes(""));

        ILayerZeroEndpoint(layerZeroEndpoint).send{ value: estimatedFee }(   // only estimatedFee forwarded
            dstChainId, remoteAndLocalAddresses, _payload, payable(msg.sender), address(0x0), bytes("")
        );
        ...
    }
    // msg.value - Σ estimatedFee remains in contract with no recovery path
}
``` [2](#0-1) 

The contract has no `receive()` or `fallback()` function and no ETH withdrawal utility. [3](#0-2) 

### Impact Explanation
Any ETH sent to `updateRate()` in excess of the sum of on-chain estimated fees is permanently frozen in the contract. There is no owner sweep, no `receive()` fallback that could be used to drain it, and no other function that moves the contract's native ETH balance. This constitutes permanent freezing of funds for any caller who over-estimates the required fee (a common defensive practice when interacting with cross-chain messaging).

Impact: **Low — Contract fails to deliver promised returns (refund of excess ETH), and the excess is permanently lost.**

### Likelihood Explanation
`updateRate()` has no access control — any external account can call it. Callers who wish to ensure the transaction succeeds often send a small buffer above the estimated fee. Because `estimateFees()` is a view call that can be queried off-chain, callers frequently add a safety margin. Every such call with `msg.value > Σ estimatedFee` results in locked ETH. The function is expected to be called regularly (rate updates), making repeated small losses realistic over the protocol's lifetime.

### Recommendation
Add an ETH refund to `msg.sender` at the end of `updateRate()` for any unused balance:

```solidity
function updateRate() external payable nonReentrant {
    // ... existing loop ...
    uint256 remaining = address(this).balance;
    if (remaining > 0) {
        (bool ok,) = payable(msg.sender).call{value: remaining}("");
        require(ok, "ETH refund failed");
    }
}
```

Alternatively, compute the total required fee before the loop and `require(msg.value == totalFee)` to prevent over-payment entirely.

### Proof of Concept
1. `MultiChainRateProvider` has two registered rate receivers on different chains.
2. Off-chain, a caller queries `estimateTotalFee()` and gets `X` wei.
3. The caller calls `updateRate{value: X + 1000}()` (adding a 1000 wei buffer for safety).
4. The loop sends exactly `estimatedFee_1 + estimatedFee_2 = X` to LayerZero.
5. The remaining `1000 wei` stays in the contract.
6. No function exists to recover it. The ETH is permanently locked. [4](#0-3)

### Citations

**File:** contracts/cross-chain/MultiChainRateProvider.sol (L13-15)
```text
abstract contract MultiChainRateProvider is Ownable, ReentrancyGuard {
    /// @notice Last rate updated on the provider
    uint256 public rate;
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

**File:** contracts/cross-chain/MultiChainRateProvider.sol (L152-173)
```text
    /// @notice Estimate the fees of sending an update to all chains/receiver contracts
    /// @return totalEstimatedFee the total estimated fee
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
