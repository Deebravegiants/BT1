The full contract code is now available. Let me analyze the exact flow.

**Key observations:**

1. `updateRate()` has no access control — any caller can invoke it with any `msg.value`. [1](#0-0) 

2. Inside the loop, the contract calls `estimateFees()` per receiver and forwards **only `estimatedFee`** (not `msg.value`) to the LZ endpoint for each send: [2](#0-1) 

3. Total ETH forwarded to LZ = `sum(estimatedFee_i)`. If `msg.value > sum(estimatedFee_i)`, the difference stays in the `MultiChainRateProvider` contract.

4. The contract has no `receive()`, no `fallback()`, and no ETH withdrawal function — the excess is permanently locked. [3](#0-2) 

5. Contrast with the single-receiver `CrossChainRateProvider.updateRate()`, which passes the **entire `msg.value`** to LZ (letting LZ refund excess to `msg.sender`): [4](#0-3) 

---

### Title
Excess ETH sent to `updateRate()` is permanently locked — (`contracts/cross-chain/MultiChainRateProvider.sol`)

### Summary
`MultiChainRateProvider.updateRate()` is a public payable function that forwards only the per-receiver `estimatedFee` to the LayerZero endpoint for each receiver, not the full `msg.value`. Any ETH beyond the sum of estimated fees is permanently trapped in the contract, which has no withdrawal path.

### Finding Description
In `updateRate()`, the loop queries `estimateFees()` per receiver and calls `send{ value: estimatedFee }(...)` for each one:

```solidity
(uint256 estimatedFee,) = ILayerZeroEndpoint(layerZeroEndpoint)
    .estimateFees(dstChainId, address(this), _payload, false, bytes(""));

ILayerZeroEndpoint(layerZeroEndpoint).send{ value: estimatedFee }(
    dstChainId, remoteAndLocalAddresses, _payload, payable(msg.sender), address(0x0), bytes("")
);
``` [2](#0-1) 

The total ETH consumed is `Σ estimatedFee_i`. Any `msg.value` in excess of this sum is never forwarded and never refunded — it accumulates in the contract. The contract declares no `receive()` or `fallback()` function and provides no owner-callable ETH rescue function. [5](#0-4) 

The single-receiver sibling `CrossChainRateProvider` avoids this by passing the full `msg.value` to LZ, which then refunds the excess to `msg.sender`: [4](#0-3) 

### Impact Explanation
**Critical — Permanent freezing of funds.**

Any ETH sent above the actual LZ fee sum is irrecoverably locked in `MultiChainRateProvider`. There is no owner rescue, no `selfdestruct`, and no `receive`/`fallback` that could drain it. The locked amount equals `msg.value − Σ estimatedFee_i` per call.

### Likelihood Explanation
`updateRate()` is permissionless and payable. A caller who over-estimates fees (e.g., by using `estimateTotalFee()` at a different gas price than the actual execution block, or simply by sending a round-number ETH value) will permanently lose the difference. The `estimateTotalFee()` helper itself can return a value that diverges from the sum computed inside `updateRate()` if the rate changes between the two calls, making over-payment a realistic operational scenario.

### Recommendation
Replace the per-receiver `estimatedFee` forwarding pattern with one of:

1. **Require exact payment**: compute `Σ estimatedFee_i` before the loop and `require(msg.value == totalFee)`.
2. **Refund excess**: after the loop, if `address(this).balance > 0`, send it back to `msg.sender`.
3. **Mirror the single-receiver pattern**: pass `msg.value` to the first send and let LZ handle the refund (only works for a single receiver; for multiple receivers, option 1 or 2 is cleaner).

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// Assume MockLZEndpoint charges 0.001 ETH per send and refunds nothing to the provider.
// Deploy RSETHMultiChainRateProvider with 2 receivers.
// Total LZ fee = 0.002 ETH.

provider.updateRate{value: 1 ether}();

// After the call:
assert(address(provider).balance == 0.998 ether); // locked forever
// No function exists to recover it.
```

The `estimateTotalFee()` view function confirms the expected fee sum, making it straightforward to demonstrate the gap between `msg.value` and actual consumption on a local fork. [6](#0-5)

### Citations

**File:** contracts/cross-chain/MultiChainRateProvider.sol (L1-182)
```text
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

import { Ownable } from "@openzeppelin/contracts/access/Ownable.sol";
import { ReentrancyGuard } from "@openzeppelin/contracts/security/ReentrancyGuard.sol";

import { ILayerZeroEndpoint } from "contracts/external/layerzero/interfaces/ILayerZeroEndpoint.sol";

/// @title Multi chain rate provider. By witherblock reference: https://github.com/witherblock/gyarados
/// @notice Provides a rate to a multiple receiver contracts on a different chain than the one this contract is deployed
/// on
/// @dev Powered using LayerZero, all chainId(s) references are for LayerZero chainIds and not blockchain chainIds
abstract contract MultiChainRateProvider is Ownable, ReentrancyGuard {
    /// @notice Last rate updated on the provider
    uint256 public rate;

    /// @notice Last time rate was updated
    uint256 public lastUpdated;

    /// @notice LayerZero endpoint address
    address public layerZeroEndpoint;

    /// @notice Information of which token and base token rate is being provided
    RateInfo public rateInfo;

    /// @notice Rate receivers
    RateReceiver[] public rateReceivers;

    struct RateReceiver {
        uint16 _chainId;
        address _contract;
    }

    struct RateInfo {
        string tokenSymbol;
        address tokenAddress;
        string baseTokenSymbol;
        address baseTokenAddress;
    }

    /// @notice Emitted when rate is updated
    /// @param newRate the rate that was updated
    event RateUpdated(uint256 newRate);

    /// @notice Emitted when LayerZero Endpoint is updated
    /// @param newLayerZeroEndpoint the LayerZero Endpoint address that was updated
    event LayerZeroEndpointUpdated(address newLayerZeroEndpoint);

    /// @notice Emitted when a new rate receiver is added
    /// @param newChainId the chainId of the rate receiver
    /// @param newContract the address of the rate receiver
    event RateReceiverAdded(uint16 newChainId, address newContract);

    /// @notice Emitted when a rate receiver is removed
    /// @param oldChainId the chainId of the rate receiver
    /// @param oldContract the address of the rate receiver
    event RateReceiverRemoved(uint16 oldChainId, address oldContract);

    /// @notice Updates the LayerZero Endpoint address
    /// @dev Can only be called by owner
    /// @param _layerZeroEndpoint the new layer zero endpoint address
    function updateLayerZeroEndpoint(address _layerZeroEndpoint) external onlyOwner {
        layerZeroEndpoint = _layerZeroEndpoint;

        emit LayerZeroEndpointUpdated(_layerZeroEndpoint);
    }

    /// @notice Adds a rate receiver
    /// @dev Can only be called by owner
    /// @param _chainId rate receiver chainId
    /// @param _contract rate receiver address
    function addRateReceiver(uint16 _chainId, address _contract) external onlyOwner {
        rateReceivers.push(RateReceiver({ _chainId: _chainId, _contract: _contract }));

        emit RateReceiverAdded(_chainId, _contract);
    }

    /// @notice Removes a rate receiver
    /// @dev Can only be called by owner
    /// @param _index the index of the rate receiver
    function removeRateReceiver(uint256 _index) external onlyOwner {
        // Store the rate receiver in a memory var
        RateReceiver memory _rateReceiverToBeRemoved = rateReceivers[_index];

        // Get the current length of all the rate receivers
        uint256 rateReceiversLength = rateReceivers.length;

        // Get the last index of the all the rate receivers
        uint256 lastIndex = rateReceiversLength - 1;

        if (lastIndex != _index) {
            // Get the last rate receiver
            RateReceiver memory lastValue = rateReceivers[lastIndex];

            // Replace the index value with the last index value
            rateReceivers[_index] = lastValue;
        }

        rateReceivers.pop();

        emit RateReceiverRemoved(_rateReceiverToBeRemoved._chainId, _rateReceiverToBeRemoved._contract);
    }

    /// @notice Updates rate in this contract and on the receivers
    /// @dev This function is set to payable to pay for gas on execute lzReceive (on the receiver contract)
    /// on the destination chain. To compute the correct value to send check here -
    /// https://layerzero.gitbook.io/docs/evm-guides/code-examples/estimating-message-fees
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

    /// @notice Estimate the fees of sending an update to a receiver contract for a
    /// particular destination chain id
    /// @param _dstChainId desitnation chainId
    /// @return estimatedFee the estimated fee
    function estimateFees(uint16 _dstChainId) external view returns (uint256 estimatedFee) {
        uint256 latestRate = getLatestRate();

        bytes memory _payload = abi.encode(latestRate);

        (estimatedFee,) =
            ILayerZeroEndpoint(layerZeroEndpoint).estimateFees(_dstChainId, address(this), _payload, false, bytes(""));
    }

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

    /// @notice Returns the rate receivers
    function getRateReceivers() external view returns (RateReceiver[] memory) {
        return rateReceivers;
    }

    /// @notice Returns the latest rate
    function getLatestRate() public view virtual returns (uint256) { }
}
```

**File:** contracts/cross-chain/CrossChainRateProvider.sol (L96-98)
```text
        ILayerZeroEndpoint(layerZeroEndpoint).send{ value: msg.value }(
            dstChainId, remoteAndLocalAddresses, _payload, payable(msg.sender), address(0x0), bytes("")
        );
```
