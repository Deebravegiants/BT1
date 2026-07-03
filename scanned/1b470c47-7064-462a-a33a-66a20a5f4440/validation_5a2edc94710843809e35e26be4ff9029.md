### Title
Hardcoded `DEFAULT_GAS_LIMIT` constant in OP-Stack messenger contracts can permanently block ETH bridging to L1 if bridge protocol reduces its maximum gas limit - (File: contracts/bridges/BaseMessenger.sol, contracts/bridges/OptimismMessenger.sol, contracts/bridges/UnichainMessenger.sol)

---

### Summary

`BaseMessenger`, `OptimismMessenger`, and `UnichainMessenger` each declare `DEFAULT_GAS_LIMIT = 200_000` as an immutable Solidity `constant`. This value is passed directly as the `_minGasLimit` argument to the OP-Stack `bridgeETHTo()` call. Because it is a `constant`, it cannot be updated without a full contract redeployment. If the OP-Stack bridge operators reduce the protocol's maximum allowed gas limit below 200,000 (a configurable governance parameter), every call to `sendETHToL1ViaBridge` will revert, permanently blocking the ETH bridging path from L2 to L1.

---

### Finding Description

All three messenger contracts share the same pattern:

```solidity
// BaseMessenger.sol, OptimismMessenger.sol, UnichainMessenger.sol
uint32 public constant DEFAULT_GAS_LIMIT = 200_000;

function sendETHToL1ViaBridge(address l2bridge, address target, uint256 value)
    external payable nonReentrant
{
    if (msg.value != value) revert MismatchedMsgValue();
    IBaseMessenger(l2bridge).bridgeETHTo{ value: value }(target, DEFAULT_GAS_LIMIT, bytes(""));
}
``` [1](#0-0) [2](#0-1) [3](#0-2) 

The `_minGasLimit` parameter passed to `bridgeETHTo` is validated by the OP-Stack `OptimismPortal` / `ResourceMetering` layer against a protocol-level maximum resource limit. This maximum is a governance-configurable parameter in the OP-Stack `SystemConfig` contract. If the bridge operators reduce the maximum below 200,000, the `depositTransaction` call inside `bridgeETHTo` will revert with every invocation of `sendETHToL1ViaBridge`.

Unlike `L1VaultV2.ccipGasLimit`, which is correctly made configurable via `setCcipGasLimit`: [4](#0-3) 

…the messenger gas limits are `constant` and offer no setter or upgrade path short of full redeployment.

---

### Impact Explanation

ETH deposited by users into L2 pool contracts (e.g., `RSETHPoolV3`) accumulates in the pool and is periodically moved to L1 for restaking via the BRIDGER role calling `moveAssetsForBridging` followed by `sendETHToL1ViaBridge`. If the bridge call reverts, the ETH remains locked in the L2 pool contract indefinitely — users cannot retrieve it and it cannot be restaked. This constitutes **temporary freezing of funds** (Medium severity per the allowed impact scope).

---

### Likelihood Explanation

The OP-Stack `SystemConfig.gasLimit` and the `ResourceMetering` maximum are governance-controlled parameters that the bridge operators (Optimism Foundation, Base, Unichain teams) can adjust through standard upgrade procedures. While a reduction below 200,000 is unlikely under normal operations, it is a realistic governance action (e.g., during a network upgrade or gas repricing event), exactly analogous to GMX's `Keys.MAX_CALLBACK_GAS_LIMIT` being reduced. The root cause — the hardcoded `constant` — exists entirely within LRT-rsETH's own codebase and is independently fixable.

---

### Recommendation

Replace the `constant` with a mutable state variable and add a privileged setter, mirroring the pattern already used in `L1VaultV2`:

```solidity
// Before (broken pattern)
uint32 public constant DEFAULT_GAS_LIMIT = 200_000;

// After (recommended)
uint32 public defaultGasLimit = 200_000;

function setDefaultGasLimit(uint32 _gasLimit) external onlyOwner {
    defaultGasLimit = _gasLimit;
}
```

This allows the protocol to respond to any bridge-side configuration change without requiring a contract redeployment.

---

### Proof of Concept

1. User deposits ETH into `RSETHPoolV3` on Base/Optimism/Unichain.
2. BRIDGER calls `moveAssetsForBridging(amount)` — ETH leaves the pool and is sent to the BRIDGER.
3. BRIDGER calls `BaseMessenger.sendETHToL1ViaBridge(l2bridge, l1Vault, amount)`.
4. Internally: `IBaseMessenger(l2bridge).bridgeETHTo{value: amount}(l1Vault, 200_000, "")`.
5. The OP-Stack bridge validates `200_000` against its current maximum gas limit.
6. If the bridge's maximum has been reduced below `200_000` via governance, the call reverts.
7. ETH is now stuck: it has already left the pool (step 2) and cannot reach L1. The BRIDGER holds it but cannot bridge it. All subsequent bridging attempts revert identically until the contract is redeployed with a corrected value. [5](#0-4) [6](#0-5) [7](#0-6)

### Citations

**File:** contracts/bridges/BaseMessenger.sol (L15-26)
```text
    uint32 public constant DEFAULT_GAS_LIMIT = 200_000;

    /**
     * @notice Bridge ETH from Base L2 to Ethereum Mainnet
     * @param l2bridge The address of the L2 bridge on Base
     * @param target The address of the target contract on L1
     * @param value The amount of ETH to send
     */
    function sendETHToL1ViaBridge(address l2bridge, address target, uint256 value) external payable nonReentrant {
        if (msg.value != value) revert MismatchedMsgValue();
        IBaseMessenger(l2bridge).bridgeETHTo{ value: value }(target, DEFAULT_GAS_LIMIT, bytes(""));
    }
```

**File:** contracts/bridges/OptimismMessenger.sol (L15-27)
```text
    /// @notice The recommended gas limit for sending ETH to L1 via the Optimism bridge
    uint32 public constant DEFAULT_GAS_LIMIT = 200_000;

    /**
     * @notice Bridge ETH from Optimism L2 to Ethereum Mainnet
     * @param l2bridge The address of the L2 bridge on Optimism
     * @param target The address of the target contract on L1
     * @param value The amount of ETH to send
     */
    function sendETHToL1ViaBridge(address l2bridge, address target, uint256 value) external payable nonReentrant {
        if (msg.value != value) revert MismatchedMsgValue();
        IOptimismMessenger(l2bridge).bridgeETHTo{ value: value }(target, DEFAULT_GAS_LIMIT, bytes(""));
    }
```

**File:** contracts/bridges/UnichainMessenger.sol (L15-27)
```text
    /// @notice The recommended gas limit for sending ETH to L1 via the Unichain bridge
    uint32 public constant DEFAULT_GAS_LIMIT = 200_000;

    /**
     * @notice Bridge ETH from Unichain L2 to Ethereum Mainnet
     * @param l2bridge The address of the L2 bridge on Unichain
     * @param target The address of the target contract on L1
     * @param value The amount of ETH to send
     */
    function sendETHToL1ViaBridge(address l2bridge, address target, uint256 value) external payable nonReentrant {
        if (msg.value != value) revert MismatchedMsgValue();
        IUnichainMessenger(l2bridge).bridgeETHTo{ value: value }(target, DEFAULT_GAS_LIMIT, bytes(""));
    }
```

**File:** contracts/L1VaultV2.sol (L554-559)
```text
    function setCcipGasLimit(uint256 _ccipGasLimit) external onlyRole(TIMELOCK_ROLE) {
        if (_ccipGasLimit == 0) {
            revert InvalidCcipGasLimit();
        }
        ccipGasLimit = _ccipGasLimit;
        emit CcipGasLimitSet(_ccipGasLimit);
```
