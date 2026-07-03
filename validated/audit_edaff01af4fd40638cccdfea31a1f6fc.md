### Title
Single-Step Ownership Transfer in Rate Oracle Contracts Can Permanently Lock Configuration — (`contracts/cross-chain/CrossChainRateProvider.sol`, `contracts/cross-chain/CrossChainRateReceiver.sol`, `contracts/cross-chain/MultiChainRateProvider.sol`)

---

### Summary

`CrossChainRateProvider`, `CrossChainRateReceiver`, and `MultiChainRateProvider` inherit from OpenZeppelin's single-step `Ownable` rather than `Ownable2Step`. A single erroneous `transferOwnership` call to an address for which the caller does not hold the private key permanently and irrecoverably strips the owner role, locking all owner-gated configuration functions forever. Because these contracts govern the rate oracle infrastructure that L2 pools rely on for pricing, the loss of owner control can permanently freeze the ability to update the rate provider, endpoint, or receiver list, eventually causing the on-chain rate to become permanently stale.

---

### Finding Description

All three contracts import and inherit from `@openzeppelin/contracts/access/Ownable.sol`: [1](#0-0) [2](#0-1) [3](#0-2) 

OZ's `Ownable.transferOwnership` immediately overwrites `_owner` with the supplied address in a single transaction, with only a zero-address guard: [4](#0-3) 

There is no pending-owner pattern, no confirmation step, and no way to recover if the wrong address is supplied.

The owner-gated functions that become permanently inaccessible upon ownership loss are:

**`CrossChainRateProvider`**
- `updateLayerZeroEndpoint` — controls which LZ endpoint is used to send rate messages [5](#0-4) 
- `updateRateReceiver` — controls which L2 contract receives the rate [6](#0-5) 
- `updateDstChainId` — controls the destination chain [7](#0-6) 

**`CrossChainRateReceiver`**
- `updateRateProvider` — controls which L1 address is trusted to push rates; if this becomes wrong, `lzReceive` permanently rejects all incoming rate messages [8](#0-7) 
- `updateLayerZeroEndpoint` — controls which LZ endpoint is trusted to call `lzReceive` [9](#0-8) 

The `lzReceive` function enforces both checks: [10](#0-9) 

If either `layerZeroEndpoint` or `rateProvider` can no longer be corrected (because the owner is lost), any future LZ endpoint migration or rate-provider contract upgrade permanently breaks rate delivery to every L2 pool that reads from this receiver.

**`MultiChainRateProvider`**
- `updateLayerZeroEndpoint` — same endpoint lock risk [11](#0-10) 
- `addRateReceiver` / `removeRateReceiver` — the list of destination chains/contracts can never be modified [12](#0-11) 

---

### Impact Explanation

If ownership is transferred to an uncontrolled address:

1. The rate oracle configuration is permanently frozen.
2. When LayerZero migrates its endpoint (a documented, recurring event in LZ history), neither the provider nor the receiver can be updated. `updateRate()` calls on the provider will revert (wrong endpoint), and `lzReceive` calls on the receiver will revert (wrong endpoint check). The stored `rate` on the receiver becomes permanently stale.
3. L2 pools that call `getRate()` on the receiver will return a stale rate, causing all subsequent deposits and withdrawals to be priced incorrectly — users receive fewer or more pool tokens than the true rsETH/ETH rate warrants.
4. Redeployment of the receiver contract is the only remedy, requiring coordinated migration of every pool that references it.

**Impact: Low — Contract fails to deliver promised returns (stale rate pricing), escalating to Medium (temporary freezing of funds) if the pool enforces a freshness check on the rate.**

---

### Likelihood Explanation

Likelihood is low. It requires the owner to supply an incorrect address to `transferOwnership`. However, this is precisely the scenario the original report describes as realistic: a typo, a copy-paste error, or a hardware-wallet address mismatch during a routine ownership handoff. The absence of any confirmation step means there is no safety net.

---

### Recommendation

Replace `Ownable` with `Ownable2Step` in all three contracts:

```solidity
// Before
import { Ownable } from "@openzeppelin/contracts/access/Ownable.sol";
contract CrossChainRateProvider is Ownable, ReentrancyGuard { ... }

// After
import { Ownable2Step } from "@openzeppelin/contracts/access/Ownable2Step.sol";
contract CrossChainRateProvider is Ownable2Step, ReentrancyGuard { ... }
```

`Ownable2Step.transferOwnership` only sets a `_pendingOwner`; the new owner must call `acceptOwnership()` from the correct address to complete the transfer. An incorrect pending owner can be overwritten before acceptance, and the current owner retains control throughout. [13](#0-12) 

---

### Proof of Concept

1. Owner of `CrossChainRateReceiver` calls `transferOwnership(0xDeadAddress)` — a typo or clipboard error.
2. `_owner` is immediately set to `0xDeadAddress`. The previous owner has no recourse.
3. LayerZero later migrates its endpoint to a new address (as it did with V1→V2).
4. `updateLayerZeroEndpoint` is called — reverts: `"Ownable: caller is not the owner"`.
5. All subsequent `lzReceive` calls revert: `"Sender should be lz endpoint"` (old endpoint no longer calls the contract).
6. `rate` on the receiver is permanently frozen at its last value.
7. Every L2 pool reading `getRate()` from this receiver prices all deposits and withdrawals against a stale rate indefinitely.
8. The only fix is redeploying the receiver and migrating all dependent pools — equivalent to the "restart from scratch" impact described in the original report.

### Citations

**File:** contracts/cross-chain/CrossChainRateProvider.sol (L4-12)
```text
import { Ownable } from "@openzeppelin/contracts/access/Ownable.sol";
import { ReentrancyGuard } from "@openzeppelin/contracts/security/ReentrancyGuard.sol";

import { ILayerZeroEndpoint } from "contracts/external/layerzero/interfaces/ILayerZeroEndpoint.sol";

/// @title Cross chain rate provider. By witherblock reference: https://github.com/witherblock/gyarados
/// @notice Provides a rate to a receiver contract on a different chain than the one this contract is deployed on
/// @dev Powered using LayerZero
abstract contract CrossChainRateProvider is Ownable, ReentrancyGuard {
```

**File:** contracts/cross-chain/CrossChainRateProvider.sol (L57-61)
```text
    function updateLayerZeroEndpoint(address _layerZeroEndpoint) external onlyOwner {
        layerZeroEndpoint = _layerZeroEndpoint;

        emit LayerZeroEndpointUpdated(_layerZeroEndpoint);
    }
```

**File:** contracts/cross-chain/CrossChainRateProvider.sol (L66-70)
```text
    function updateRateReceiver(address _rateReceiver) external onlyOwner {
        rateReceiver = _rateReceiver;

        emit RateReceiverUpdated(_rateReceiver);
    }
```

**File:** contracts/cross-chain/CrossChainRateProvider.sol (L75-79)
```text
    function updateDstChainId(uint16 _dstChainId) external onlyOwner {
        dstChainId = _dstChainId;

        emit DstChainIdUpdated(_dstChainId);
    }
```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L4-11)
```text
import { Ownable } from "@openzeppelin/contracts/access/Ownable.sol";

import { ILayerZeroReceiver } from "contracts/external/layerzero/interfaces/ILayerZeroReceiver.sol";

/// @title Cross chain rate receiver. By witherblock reference: https://github.com/witherblock/gyarados
/// @notice Receives a rate from a provider contract on a different chain than the one this contract is deployed on
/// @dev Powered using LayerZero
abstract contract CrossChainRateReceiver is ILayerZeroReceiver, Ownable {
```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L54-58)
```text
    function updateLayerZeroEndpoint(address _layerZeroEndpoint) external onlyOwner {
        layerZeroEndpoint = _layerZeroEndpoint;

        emit LayerZeroEndpointUpdated(_layerZeroEndpoint);
    }
```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L63-67)
```text
    function updateRateProvider(address _rateProvider) external onlyOwner {
        rateProvider = _rateProvider;

        emit RateProviderUpdated(_rateProvider);
    }
```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L82-92)
```text
    function lzReceive(uint16 _srcChainId, bytes memory _srcAddress, uint64, bytes calldata _payload) external {
        require(msg.sender == layerZeroEndpoint, "Sender should be lz endpoint");

        address srcAddress;
        assembly {
            srcAddress := mload(add(_srcAddress, 20))
        }

        require(_srcChainId == srcChainId, "Src chainId must be correct");
        require(srcAddress == rateProvider, "Src address must be provider");

```

**File:** contracts/cross-chain/MultiChainRateProvider.sol (L4-13)
```text
import { Ownable } from "@openzeppelin/contracts/access/Ownable.sol";
import { ReentrancyGuard } from "@openzeppelin/contracts/security/ReentrancyGuard.sol";

import { ILayerZeroEndpoint } from "contracts/external/layerzero/interfaces/ILayerZeroEndpoint.sol";

/// @title Multi chain rate provider. By witherblock reference: https://github.com/witherblock/gyarados
/// @notice Provides a rate to a multiple receiver contracts on a different chain than the one this contract is deployed
/// on
/// @dev Powered using LayerZero, all chainId(s) references are for LayerZero chainIds and not blockchain chainIds
abstract contract MultiChainRateProvider is Ownable, ReentrancyGuard {
```

**File:** contracts/cross-chain/MultiChainRateProvider.sol (L62-66)
```text
    function updateLayerZeroEndpoint(address _layerZeroEndpoint) external onlyOwner {
        layerZeroEndpoint = _layerZeroEndpoint;

        emit LayerZeroEndpointUpdated(_layerZeroEndpoint);
    }
```

**File:** contracts/cross-chain/MultiChainRateProvider.sol (L72-76)
```text
    function addRateReceiver(uint16 _chainId, address _contract) external onlyOwner {
        rateReceivers.push(RateReceiver({ _chainId: _chainId, _contract: _contract }));

        emit RateReceiverAdded(_chainId, _contract);
    }
```

**File:** lib/openzeppelin-contracts/contracts/access/Ownable.sol (L69-77)
```text
    function transferOwnership(address newOwner) public virtual onlyOwner {
        require(newOwner != address(0), "Ownable: new owner is the zero address");
        _transferOwnership(newOwner);
    }

    /**
     * @dev Transfers ownership of the contract to a new account (`newOwner`).
     * Internal function without access restriction.
     */
```

**File:** lib/openzeppelin-contracts/contracts/access/Ownable2Step.sol (L35-56)
```text
    function transferOwnership(address newOwner) public virtual override onlyOwner {
        _pendingOwner = newOwner;
        emit OwnershipTransferStarted(owner(), newOwner);
    }

    /**
     * @dev Transfers ownership of the contract to a new account (`newOwner`) and deletes any pending owner.
     * Internal function without access restriction.
     */
    function _transferOwnership(address newOwner) internal virtual override {
        delete _pendingOwner;
        super._transferOwnership(newOwner);
    }

    /**
     * @dev The new owner accepts the ownership transfer.
     */
    function acceptOwnership() public virtual {
        address sender = _msgSender();
        require(pendingOwner() == sender, "Ownable2Step: caller is not the new owner");
        _transferOwnership(sender);
    }
```
