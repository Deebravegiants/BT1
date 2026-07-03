### Title
ETH Permanently Locked in `MultiChainRateProvider` — No Withdrawal Function for Excess `msg.value` - (File: contracts/cross-chain/MultiChainRateProvider.sol)

### Summary
The `updateRate()` function in `MultiChainRateProvider` is `payable` and accepts ETH from callers to pay LayerZero messaging fees. However, it only forwards the on-chain `estimatedFee` per receiver — not the full `msg.value`. Any ETH sent beyond the sum of estimated fees is permanently locked in the contract, which has no withdrawal function.

### Finding Description
`MultiChainRateProvider.updateRate()` is marked `payable` and iterates over all registered `rateReceivers`, calling `ILayerZeroEndpoint.estimateFees()` on-chain for each and forwarding exactly that `estimatedFee` to the LayerZero endpoint:

```solidity
(uint256 estimatedFee,) = ILayerZeroEndpoint(layerZeroEndpoint)
    .estimateFees(dstChainId, address(this), _payload, false, bytes(""));

ILayerZeroEndpoint(layerZeroEndpoint).send{ value: estimatedFee }(
    dstChainId, remoteAndLocalAddresses, _payload, payable(msg.sender), address(0x0), bytes("")
);
``` [1](#0-0) 

If `msg.value > Σ(estimatedFee_i)`, the difference is silently retained by the contract. The abstract contract defines no `receive()` fallback, no ETH sweep, and no withdrawal function of any kind. The two concrete deployed implementations — `RSETHMultiChainRateProvider` and `AGETHMultiChainRateProvider` — inherit this abstract contract and add no withdrawal mechanism either. [2](#0-1) [3](#0-2) 

By contrast, `CrossChainRateProvider.updateRate()` forwards the entire `msg.value` directly (`send{ value: msg.value }`), so no ETH is stranded there. [4](#0-3) 

### Impact Explanation
Any ETH sent to `updateRate()` in excess of the total LayerZero fees is permanently frozen in the contract. There is no owner-callable sweep, no `receive()` refund path, and no upgrade path that would recover the funds. This matches the "permanent freezing of funds" impact class.

**Impact: Critical — Permanent freezing of funds.**

### Likelihood Explanation
`updateRate()` has no access control — any address may call it. Callers must supply ETH to cover LayerZero fees across all registered receivers. Because fee estimation is done on-chain at call time, callers routinely send a small buffer above the expected total to avoid reverts from fee fluctuations. Every such call with a non-zero buffer permanently locks that excess. The more receivers are registered, the larger the typical buffer and the more ETH accumulates. This is a realistic, recurring scenario for any active rate-update caller.

### Recommendation
Add a refund of unused ETH at the end of `updateRate()`:

```solidity
// after the loop
uint256 remaining = address(this).balance;
if (remaining > 0) {
    (bool ok,) = payable(msg.sender).call{value: remaining}("");
    require(ok, "ETH refund failed");
}
```

Alternatively, remove the `payable` modifier and require callers to pass the exact fee amount, or add an owner-only ETH recovery function.

### Proof of Concept
1. Deploy `RSETHMultiChainRateProvider` (or `AGETHMultiChainRateProvider`) with two registered receivers.
2. Off-chain, estimate total fees = 0.01 ETH. Call `updateRate{value: 0.011 ether}()`.
3. The loop sends exactly `estimatedFee` (≈0.005 ETH) to each receiver via LayerZero.
4. The remaining 0.001 ETH stays in the contract.
5. Confirm `address(multiChainRateProvider).balance == 0.001 ether` after the call.
6. Attempt any withdrawal — no function exists. ETH is permanently locked. [5](#0-4)

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
