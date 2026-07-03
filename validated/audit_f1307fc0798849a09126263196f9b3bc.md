The vulnerability is real. Here is the full analysis:

---

### Title
Excess ETH sent to `updateRate()` is permanently locked — no refund path exists — (`contracts/cross-chain/MultiChainRateProvider.sol`)

### Summary
`updateRate()` is `payable` and forwards exactly `estimatedFee` per receiver to the LayerZero endpoint. Any ETH remaining after those sends (`msg.value − Σ estimatedFees`) stays in the contract forever because the contract has no `receive()`, no `fallback()`, and no ETH-sweep/rescue function.

### Finding Description

`updateRate()` is declared `payable` with no access control: [1](#0-0) 

Inside the loop, the contract queries the exact fee and forwards only that amount to LZ: [2](#0-1) 

The `payable(msg.sender)` argument is the **LZ refund address** — it tells LZ to refund any per-send excess back to the caller. It does **not** cause the contract itself to refund the difference between `msg.value` and `Σ estimatedFees`.

After the loop ends, any ETH in excess of the sum of all `estimatedFee` values remains in the contract's balance. The contract defines no mechanism to recover it:

- No `receive()` or `fallback()` function. [3](#0-2) 
- No owner-callable ETH withdrawal or sweep function. [4](#0-3) 

### Impact Explanation
Any ETH overpaid by a caller accumulates in the contract and is irrecoverable. Because `updateRate()` has no access control, any address can call it and lose ETH this way. The locked ETH has no recovery path — **permanent freezing of funds**.

### Likelihood Explanation
Callers routinely overpay gas/fee estimates to avoid reverts due to fee fluctuations. The contract even exposes `estimateTotalFee()` as a guide, but that value is a snapshot; actual fees at send-time may be lower, and callers padding their `msg.value` will lose the difference. This is a normal, expected usage pattern.

### Recommendation
After the send loop, refund any remaining ETH to the caller:

```solidity
uint256 remaining = address(this).balance;
if (remaining > 0) {
    (bool ok, ) = payable(msg.sender).call{value: remaining}("");
    require(ok, "ETH refund failed");
}
```

Alternatively, add an owner-callable ETH rescue function, or compute the exact total fee before the loop and `require(msg.value == totalFee)`.

### Proof of Concept

```solidity
// Pseudocode unit test (local/fork)
uint256 totalFee = provider.estimateTotalFee();
uint256 overpay  = totalFee * 10;

uint256 balBefore = address(provider).balance;
provider.updateRate{value: overpay}();
uint256 balAfter  = address(provider).balance;

// ETH is locked — no sweep function exists
assert(balAfter > balBefore);
assert(balAfter - balBefore == overpay - totalFee);
// No function on the contract can recover balAfter
```

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
