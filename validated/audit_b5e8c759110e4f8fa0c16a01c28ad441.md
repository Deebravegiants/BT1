### Title
Excess ETH Permanently Stuck in `MultiChainRateProvider` Due to Missing ETH Recovery Mechanism - (File: contracts/cross-chain/MultiChainRateProvider.sol)

---

### Summary

`MultiChainRateProvider` is a LayerZero-powered abstract contract that accepts ETH via its `payable` `updateRate()` function to pay cross-chain messaging fees. When a caller sends more ETH than the sum of per-receiver `estimatedFee` values, the excess ETH is permanently locked in the contract with no recovery path. The contract inherits only from `Ownable` and `ReentrancyGuard`, providing no `recoverETH()`, no `receive()` with a sweep, and no admin withdrawal function.

---

### Finding Description

`MultiChainRateProvider.updateRate()` iterates over all registered `rateReceivers`, estimates the LayerZero fee for each, and sends exactly `estimatedFee` per receiver: [1](#0-0) 

The function is `payable` and accepts arbitrary `msg.value`. After the loop, any `msg.value` in excess of `sum(estimatedFee_i)` remains in the contract's balance. There is no mechanism to retrieve it:

- No `recoverETH()` function
- No `receive()` function with a sweep
- No admin withdrawal of any kind
- Inherits only `Ownable` + `ReentrancyGuard` [2](#0-1) 

The two concrete production deployments that inherit this abstract contract are:

- `RSETHMultiChainRateProvider` [3](#0-2) 
- `AGETHMultiChainRateProvider` [4](#0-3) 

Both inherit the same `updateRate()` and the same absence of any ETH recovery path.

By contrast, `LineaMessenger` and `SonicChainNativeTokenBridge` — other fee-paying bridge helpers in the same codebase — correctly inherit `Recoverable` or implement their own `recoverETH()`: [5](#0-4) [6](#0-5) 

---

### Impact Explanation

Any ETH sent to `updateRate()` beyond the exact sum of LayerZero estimated fees is permanently frozen in the contract. Because fee estimation is done on-chain at call time and callers routinely overpay to ensure the transaction succeeds (especially when gas prices fluctuate), this is a realistic accumulation path. Once stuck, the ETH cannot be recovered by any role — owner, admin, or otherwise. This constitutes **permanent freezing of funds** at Medium severity.

---

### Likelihood Explanation

`updateRate()` is a public `payable` function callable by anyone. Callers must estimate the total fee off-chain before calling, and will typically send a small buffer above the estimate to avoid reverts. Every such call that overshoots leaves a residual balance. Over the operational lifetime of `RSETHMultiChainRateProvider` and `AGETHMultiChainRateProvider` (which are rate-propagation contracts expected to be called repeatedly), this residual accumulates with no recovery path.

---

### Recommendation

Add an ETH recovery function restricted to the owner, analogous to `Recoverable.recoverETH()`:

```solidity
function recoverETH(address recipient, uint256 amount) external onlyOwner {
    require(recipient != address(0));
    require(amount > 0 && address(this).balance >= amount);
    (bool success,) = payable(recipient).call{ value: amount }("");
    require(success, "Transfer failed");
}
```

Alternatively, have `MultiChainRateProvider` inherit from `Recoverable` (as `LineaMessenger` does) to gain both `recoverETH()` and `recoverTokens()` in one step.

---

### Proof of Concept

1. `RSETHMultiChainRateProvider` is deployed with two `rateReceivers` on different chains.
2. LayerZero estimates fees of 0.01 ETH each → total 0.02 ETH.
3. Caller invokes `updateRate{ value: 0.025 ETH }()`.
4. The loop sends 0.01 ETH to LayerZero for receiver 0, then 0.01 ETH for receiver 1.
5. 0.005 ETH remains in `address(this).balance`.
6. No function exists to retrieve it. `address(this).balance` grows with every such call.
7. If the contract is deprecated or replaced, all accumulated ETH is permanently lost. [7](#0-6)

### Citations

**File:** contracts/cross-chain/MultiChainRateProvider.sol (L13-13)
```text
abstract contract MultiChainRateProvider is Ownable, ReentrancyGuard {
```

**File:** contracts/cross-chain/MultiChainRateProvider.sol (L108-134)
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

**File:** contracts/bridges/LineaMessenger.sol (L15-15)
```text
contract LineaMessenger is IL2Messenger, Recoverable {
```

**File:** contracts/utils/Recoverable.sol (L64-73)
```text
    function recoverETH(address recipient, uint256 amount) external onlyRole(DEFAULT_ADMIN_ROLE) {
        UtilLib.checkNonZeroAddress(recipient);
        if (amount == 0) revert ZeroAmount();
        if (address(this).balance < amount) revert InsufficientBalance();

        (bool success,) = payable(recipient).call{ value: amount }("");
        if (!success) revert TransferFailed();

        emit ETHRecovered(recipient, amount);
    }
```
