### Title
Excess ETH Permanently Trapped in `MultiChainRateProvider.updateRate()` - (File: `contracts/cross-chain/MultiChainRateProvider.sol`)

---

### Summary

`MultiChainRateProvider.updateRate()` is a publicly callable payable function that iterates over multiple LayerZero destination chains, sending exactly the on-chain `estimatedFee` to each `ILayerZeroEndpoint.send()` call. Any ETH sent by the caller beyond the sum of all per-chain fees is never refunded and has no recovery path, permanently trapping it in the contract.

---

### Finding Description

`MultiChainRateProvider.updateRate()` accepts arbitrary `msg.value` from any caller with no access control:

```solidity
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
}
``` [1](#0-0) 

The function queries `estimateFees()` on-chain for each receiver and forwards exactly that amount to LayerZero. The `_refundAddress` (`payable(msg.sender)`) passed to LayerZero's `send()` only covers excess within LayerZero's own accounting — it does **not** cover the gap between `msg.value` and `sum(estimatedFee)` that remains in the `MultiChainRateProvider` contract itself.

There is no `receive()` fallback, no ETH sweep function, and no admin withdrawal for native ETH anywhere in the abstract contract. [2](#0-1) 

The two concrete production deployments that inherit this behavior are `RSETHMultiChainRateProvider` and `AGETHMultiChainRateProvider`. [3](#0-2) [4](#0-3) 

By contrast, `CrossChainRateProvider.updateRate()` forwards the entire `msg.value` directly to a single LayerZero `send()` call, so LayerZero's own refund mechanism handles any excess correctly. [5](#0-4) 

---

### Impact Explanation

Any ETH sent above the sum of per-chain fees is permanently frozen in the `RSETHMultiChainRateProvider` / `AGETHMultiChainRateProvider` contract. There is no recovery path. This constitutes **permanent freezing of user funds** (Critical).

---

### Likelihood Explanation

`updateRate()` carries no access control — any externally owned account or contract can call it. Callers must over-estimate `msg.value` to avoid mid-loop reverts when gas prices fluctuate between the off-chain fee quote and on-chain execution. This is a routine operational pattern, making accidental over-payment highly likely. The more rate receivers are configured, the larger the potential over-payment. [6](#0-5) 

---

### Recommendation

After the loop, compute the total fees consumed and refund the remainder to `msg.sender`:

```solidity
function updateRate() external payable nonReentrant {
    uint256 latestRate = getLatestRate();
    rate = latestRate;
    lastUpdated = block.timestamp;
    bytes memory _payload = abi.encode(latestRate);
    uint256 rateReceiversLength = rateReceivers.length;
    uint256 totalFeeUsed;

    for (uint256 i; i < rateReceiversLength;) {
        uint16 dstChainId = uint16(rateReceivers[i]._chainId);
        bytes memory remoteAndLocalAddresses =
            abi.encodePacked(rateReceivers[i]._contract, address(this));

        (uint256 estimatedFee,) = ILayerZeroEndpoint(layerZeroEndpoint)
            .estimateFees(dstChainId, address(this), _payload, false, bytes(""));

        ILayerZeroEndpoint(layerZeroEndpoint).send{ value: estimatedFee }(
            dstChainId, remoteAndLocalAddresses, _payload,
            payable(msg.sender), address(0x0), bytes("")
        );
        totalFeeUsed += estimatedFee;
        unchecked { ++i; }
    }

    uint256 excess = msg.value - totalFeeUsed;
    if (excess > 0) {
        (bool success,) = msg.sender.call{value: excess}("");
        require(success, "ETH refund failed");
    }

    emit RateUpdated(rate);
}
```

---

### Proof of Concept

1. Assume `RSETHMultiChainRateProvider` has two rate receivers configured.
2. Off-chain, a caller queries `estimateTotalFee()` → returns `0.01 ETH`.
3. Caller submits `updateRate{value: 0.015 ETH}()` to guard against gas price movement.
4. On-chain, `estimateFees()` returns `0.005 ETH` per receiver; the loop sends `0.005 + 0.005 = 0.01 ETH` to LayerZero.
5. The remaining `0.005 ETH` sits in the `MultiChainRateProvider` contract.
6. No function exists to recover it; the ETH is permanently lost to the caller. [7](#0-6)

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

**File:** contracts/cross-chain/RSETHMultiChainRateProvider.sol (L1-5)
```text
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

import { ILRTOracle } from "contracts/interfaces/ILRTOracle.sol";
import { MultiChainRateProvider } from "contracts/cross-chain/MultiChainRateProvider.sol";
```

**File:** contracts/agETH/AGETHMultiChainRateProvider.sol (L1-5)
```text
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

import { MultiChainRateProvider } from "contracts/cross-chain/MultiChainRateProvider.sol";

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
