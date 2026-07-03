### Title
`LRTConfig.pauseAll()` Always Reverts Because `LRTConfig` Lacks `PAUSER_ROLE` in Itself — (`File: contracts/LRTConfig.sol`)

---

### Summary

`LRTConfig.pauseAll()` is gated by `PAUSER_ROLE` and is intended to atomically pause all protocol contracts in an emergency. However, it internally calls `pause()` on child contracts (`LRTDepositPool`, `LRTWithdrawalManager`, `LRTOracle`, `RSETH`, and all `NodeDelegator` instances). Those child contracts use `LRTConfigRoleChecker.onlyRole(PAUSER_ROLE)`, which checks whether `msg.sender` holds `PAUSER_ROLE` in `LRTConfig`. When called from `pauseAll()`, `msg.sender` is `LRTConfig` itself — an address that is never granted `PAUSER_ROLE` — causing every `pause()` call to revert. The function is permanently broken.

---

### Finding Description

`LRTConfig.pauseAll()` is callable only by a holder of `PAUSER_ROLE`: [1](#0-0) 

It calls `pause()` on each registered contract. For example, `NodeDelegator.pause()` is protected by `LRTConfigRoleChecker.onlyRole(PAUSER_ROLE)`: [2](#0-1) 

`LRTConfigRoleChecker.onlyRole` resolves the check as: [3](#0-2) 

So when `LRTConfig` calls `nodeDelegator.pause()`, the check becomes:
```
lrtConfig.hasRole(PAUSER_ROLE, address(lrtConfig))
```

`LRTConfig.initialize()` only grants `DEFAULT_ADMIN_ROLE` to the admin; `LRTConfig` itself is never granted `PAUSER_ROLE`: [4](#0-3) 

Therefore every `pause()` call inside `pauseAll()` reverts with `CallerNotLRTConfigAllowedRole`. The `PAUSER_ROLE` holder who calls `pauseAll()` passes the outer gate but the function always fails internally — an exact structural parallel to M-14.

---

### Impact Explanation

The emergency `pauseAll()` function is permanently non-functional. In a live exploit scenario, the PAUSER_ROLE holder cannot atomically halt all protocol contracts in a single transaction. They must instead call `pause()` on each contract individually across multiple transactions. During this window, the protocol remains active and exploitable. This constitutes a **Low** impact: the contract fails to deliver its promised emergency-pause guarantee, but individual per-contract pausing remains available as a fallback.

---

### Likelihood Explanation

**High.** This is a structural, deterministic failure. Every invocation of `pauseAll()` will revert as long as `LRTConfig` is not explicitly granted `PAUSER_ROLE` in itself — which is not done anywhere in the codebase. No special conditions or attacker actions are required to trigger it.

---

### Recommendation

Grant `PAUSER_ROLE` to the `LRTConfig` contract address during `initialize()`, or refactor `pauseAll()` to use internal `_pause()` calls via a trusted intermediary pattern, or replace the per-contract role check with a direct caller whitelist that includes `LRTConfig`.

```solidity
// In LRTConfig.initialize():
_grantRole(LRTConstants.PAUSER_ROLE, address(this));
```

---

### Proof of Concept

1. Deploy the protocol. `LRTConfig` holds only `DEFAULT_ADMIN_ROLE` for the admin; no role is granted to `address(LRTConfig)`.
2. Grant `PAUSER_ROLE` to an EOA `pauser`.
3. `pauser` calls `LRTConfig.pauseAll()`.
4. The outer `onlyRole(PAUSER_ROLE)` check passes (pauser has the role).
5. `LRTConfig` calls `nodeDelegator.pause()` with `msg.sender = address(LRTConfig)`.
6. `NodeDelegator.pause()` → `LRTConfigRoleChecker.onlyRole(PAUSER_ROLE)` → `lrtConfig.hasRole(PAUSER_ROLE, address(lrtConfig))` → `false` → revert `CallerNotLRTConfigAllowedRole`.
7. `pauseAll()` reverts. No contracts are paused.

### Citations

**File:** contracts/LRTConfig.sol (L49-62)
```text
    function initialize(address admin, address stETH, address ethX, address rsETH_) external initializer {
        UtilLib.checkNonZeroAddress(admin);
        UtilLib.checkNonZeroAddress(rsETH_);

        __AccessControl_init();
        _setToken(LRTConstants.ST_ETH_TOKEN, stETH);
        _setToken(LRTConstants.ETHX_TOKEN, ethX);
        _addNewSupportedAsset(stETH, 100_000 ether);
        _addNewSupportedAsset(ethX, 100_000 ether);

        _grantRole(DEFAULT_ADMIN_ROLE, admin);

        rsETH = rsETH_;
    }
```

**File:** contracts/LRTConfig.sol (L262-285)
```text
    function pauseAll() external onlyRole(LRTConstants.PAUSER_ROLE) {
        IPausable lrtDepositPool = IPausable(getContract(LRTConstants.LRT_DEPOSIT_POOL));
        IPausable lrtWithdrawalManager = IPausable(getContract(LRTConstants.LRT_WITHDRAW_MANAGER));
        IPausable lrtOracle = IPausable(getContract(LRTConstants.LRT_ORACLE));
        IPausable rsETHContract = IPausable(rsETH);

        if (!lrtDepositPool.paused()) lrtDepositPool.pause();
        if (!lrtWithdrawalManager.paused()) lrtWithdrawalManager.pause();
        if (!lrtOracle.paused()) lrtOracle.pause();
        if (!rsETHContract.paused()) rsETHContract.pause();

        address[] memory nodeDelegatorQueue = ILRTDepositPool(address(lrtDepositPool)).getNodeDelegatorQueue();
        uint256 nodeDelegatorCount = nodeDelegatorQueue.length;

        for (uint256 i = 0; i < nodeDelegatorCount;) {
            IPausable nodeDelegator = IPausable(nodeDelegatorQueue[i]);
            if (!nodeDelegator.paused()) nodeDelegator.pause();
            unchecked {
                ++i;
            }
        }

        emit PausedAll(msg.sender);
    }
```

**File:** contracts/NodeDelegator.sol (L534-537)
```text
    /// @dev Triggers stopped state. Contract must not be paused.
    function pause() external onlyRole(LRTConstants.PAUSER_ROLE) {
        _pause();
    }
```

**File:** contracts/utils/LRTConfigRoleChecker.sol (L19-25)
```text
    modifier onlyRole(bytes32 role) {
        if (!IAccessControl(address(lrtConfig)).hasRole(role, msg.sender)) {
            string memory roleStr = string(abi.encodePacked(role));
            revert ILRTConfig.CallerNotLRTConfigAllowedRole(roleStr);
        }
        _;
    }
```
