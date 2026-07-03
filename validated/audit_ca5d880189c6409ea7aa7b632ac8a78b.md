### Title
Missing Storage Gap in `LRTConfigRoleChecker` Enables Storage Corruption on Upgrade — (File: contracts/utils/LRTConfigRoleChecker.sol)

### Summary
`LRTConfigRoleChecker` is a custom abstract base contract with one storage variable (`lrtConfig`) and **no `__gap` reserved storage**. Every major upgradeable protocol contract inherits from it. If the protocol ever adds a new state variable to `LRTConfigRoleChecker` during an upgrade, the storage layout of all inheriting contracts will be silently corrupted, breaking role-based access control and potentially freezing all protocol operations.

### Finding Description
`LRTConfigRoleChecker` declares one storage slot:

```solidity
ILRTConfig public lrtConfig; // slot 0
``` [1](#0-0) 

There is no `uint256[N] private __gap;` array. This contract is the root of the inheritance chain for every major upgradeable contract in the protocol:

| Contract | Inherits `LRTConfigRoleChecker` |
|---|---|
| `LRTDepositPool` | ✓ |
| `NodeDelegator` | ✓ |
| `RSETH` | ✓ |
| `LRTOracle` | ✓ |
| `LRTWithdrawalManager` | ✓ |
| `LRTUnstakingVault` | ✓ |
| `LRTConverter` | ✓ | [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6) [8](#0-7) 

All of these contracts are confirmed upgradeable — they call `_disableInitializers()` in their constructors and use `reinitializer(N)` for multi-step upgrades (e.g., `reinitializer(2)` and `reinitializer(3)` in `LRTWithdrawalManager`, `reinitializer(2)` in `NodeDelegator`, `LRTConverter`, `LRTOracle`, `RSETH`, and `L1Vault`). [9](#0-8) [10](#0-9) 

The current storage layout of `LRTDepositPool` (as an example) is:

| Slot | Variable | Source |
|---|---|---|
| 0 | `lrtConfig` | `LRTConfigRoleChecker` |
| 1 | `maxNodeDelegatorLimit` | `LRTDepositPool` |
| 2 | `minAmountToDeposit` | `LRTDepositPool` |
| 3 | `isNodeDelegator` (mapping) | `LRTDepositPool` |
| … | … | … | [11](#0-10) 

If a developer adds any new state variable to `LRTConfigRoleChecker` in a future upgrade (e.g., a `version` counter or a `paused` flag), `lrtConfig` shifts from slot 0 to slot 1. In the proxy's existing storage, slot 1 holds `maxNodeDelegatorLimit` (value `10`, i.e., address `0x000…000a`). After the upgrade, every call to `IAccessControl(address(lrtConfig)).hasRole(…)` would target address `0xa`, which is not a contract, causing all role-gated functions to revert or behave incorrectly.

### Impact Explanation
Storage corruption of `lrtConfig` across all inheriting contracts would:
1. Break every role check (`onlyLRTAdmin`, `onlyLRTManager`, `onlyLRTOperator`, `onlyAssetTransferRole`, `onlyRole`), making all privileged and user-facing functions revert.
2. Freeze deposits (`depositETH`, `depositAsset`), withdrawals (`initiateWithdrawal`, `completeWithdrawal`, `instantWithdrawal`), oracle updates (`updateRSETHPrice`), and unstaking operations.
3. Potentially allow unauthorized minting or burning of `rsETH` if `lrtConfig` resolves to a contract that returns `true` for `hasRole`.

This maps to **Medium — Temporary (or Permanent) Freezing of Funds**, depending on whether the corruption is recoverable.

### Likelihood Explanation
The protocol has already executed multiple upgrade cycles (evidenced by `reinitializer(2)` and `reinitializer(3)` calls across several contracts). Future upgrades to `LRTConfigRoleChecker` — e.g., adding a `paused` flag, a version field, or a new config pointer — are plausible as the protocol evolves. The risk is latent but non-theoretical: it activates the moment any developer adds a variable to the base contract without knowing about the missing gap.

### Recommendation
Add a storage gap to `LRTConfigRoleChecker` sized to reserve 50 total slots (standard OpenZeppelin convention):

```solidity
abstract contract LRTConfigRoleChecker {
    ILRTConfig public lrtConfig; // 1 slot used

    uint256[49] private __gap; // reserve remaining 49 slots
    // ...
}
``` [12](#0-11) 

### Proof of Concept
**Before upgrade** (current state):
- Proxy slot 0 = `lrtConfig` address (e.g., `0xABC…`)
- Proxy slot 1 = `maxNodeDelegatorLimit` = `10`

**After upgrade** (new variable `uint256 version` prepended to `LRTConfigRoleChecker`):
- New implementation slot 0 = `version` → reads `0xABC…` (old `lrtConfig` value) — wrong
- New implementation slot 1 = `lrtConfig` → reads `10` (old `maxNodeDelegatorLimit`) → `lrtConfig = address(10) = 0x000…000a`

Every subsequent call to `IAccessControl(address(lrtConfig)).hasRole(role, msg.sender)` targets `0x000…000a`, which has no code, causing all role-gated operations across `LRTDepositPool`, `NodeDelegator`, `RSETH`, `LRTOracle`, `LRTWithdrawalManager`, `LRTUnstakingVault`, and `LRTConverter` to revert permanently.

### Citations

**File:** contracts/utils/LRTConfigRoleChecker.sol (L12-81)
```text
abstract contract LRTConfigRoleChecker {
    ILRTConfig public lrtConfig;

    // events
    event UpdatedLRTConfig(address indexed lrtConfig);

    // modifiers
    modifier onlyRole(bytes32 role) {
        if (!IAccessControl(address(lrtConfig)).hasRole(role, msg.sender)) {
            string memory roleStr = string(abi.encodePacked(role));
            revert ILRTConfig.CallerNotLRTConfigAllowedRole(roleStr);
        }
        _;
    }

    modifier onlyLRTManager() {
        if (!IAccessControl(address(lrtConfig)).hasRole(LRTConstants.MANAGER, msg.sender)) {
            revert ILRTConfig.CallerNotLRTConfigManager();
        }
        _;
    }

    modifier onlyLRTOperator() {
        if (!IAccessControl(address(lrtConfig)).hasRole(LRTConstants.OPERATOR_ROLE, msg.sender)) {
            revert ILRTConfig.CallerNotLRTConfigOperator();
        }
        _;
    }

    modifier onlyAssetTransferRole() {
        if (!IAccessControl(address(lrtConfig)).hasRole(LRTConstants.ASSET_TRANSFER_ROLE, msg.sender)) {
            revert ILRTConfig.CallerNotLRTConfigAssetTransferRole();
        }
        _;
    }

    modifier onlyAssetTransferOrOperatorRole() {
        if (
            !IAccessControl(address(lrtConfig)).hasRole(LRTConstants.ASSET_TRANSFER_ROLE, msg.sender)
                && !IAccessControl(address(lrtConfig)).hasRole(LRTConstants.OPERATOR_ROLE, msg.sender)
        ) {
            revert ILRTConfig.CallerNotLRTConfigOperatorOrAssetTransferRole();
        }
        _;
    }

    modifier onlyLRTAdmin() {
        if (!IAccessControl(address(lrtConfig)).hasRole(LRTConstants.DEFAULT_ADMIN_ROLE, msg.sender)) {
            revert ILRTConfig.CallerNotLRTConfigAdmin();
        }
        _;
    }

    modifier onlySupportedAsset(address asset) {
        if (!lrtConfig.isSupportedAsset(asset)) {
            revert ILRTConfig.AssetNotSupported();
        }
        _;
    }

    modifier onlySupportedERC20Token(address asset) {
        if (!lrtConfig.isSupportedAsset(asset)) {
            revert ILRTConfig.AssetNotSupported();
        }
        if (asset == LRTConstants.ETH_TOKEN) {
            revert ILRTConfig.ETHNotSupported();
        }
        _;
    }
}
```

**File:** contracts/LRTDepositPool.sol (L26-26)
```text
contract LRTDepositPool is ILRTDepositPool, LRTConfigRoleChecker, PausableUpgradeable, ReentrancyGuardUpgradeable {
```

**File:** contracts/LRTDepositPool.sol (L29-36)
```text
    uint256 public maxNodeDelegatorLimit;
    uint256 public minAmountToDeposit;

    mapping(address => uint256) public isNodeDelegator; // 0: not a node delegator, 1: is a node delegator
    address[] public nodeDelegatorQueue;

    /// @notice maximum amount that can be ignored
    uint256 public maxNegligibleAmount;
```

**File:** contracts/NodeDelegator.sol (L39-39)
```text
contract NodeDelegator is INodeDelegator, LRTConfigRoleChecker, PausableUpgradeable, ReentrancyGuardUpgradeable {
```

**File:** contracts/NodeDelegator.sol (L75-77)
```text
    function initialize2() external reinitializer(2) {
        lastNonce = _getNonce();
    }
```

**File:** contracts/RSETH.sol (L13-13)
```text
contract RSETH is Initializable, LRTConfigRoleChecker, ERC20Upgradeable, PausableUpgradeable {
```

**File:** contracts/LRTOracle.sol (L23-23)
```text
contract LRTOracle is ILRTOracle, LRTConfigRoleChecker, Initializable {
```

**File:** contracts/LRTWithdrawalManager.sol (L26-31)
```text
contract LRTWithdrawalManager is
    ILRTWithdrawalManager,
    LRTConfigRoleChecker,
    PausableUpgradeable,
    ReentrancyGuardUpgradeable
{
```

**File:** contracts/LRTWithdrawalManager.sol (L109-121)
```text
    function initialize2(
        uint256 unlockedWithdrawalsCountETHx,
        uint256 unlockedWithdrawalsCountSTETH,
        uint256 unlockedWithdrawalsCountETH
    )
        external
        reinitializer(2)
        onlyRole(LRTConstants.UNLOCKED_WITHDRAWAL_INITIALIZER)
    {
        unlockedWithdrawalsCount[lrtConfig.getLSTToken(LRTConstants.ST_ETH_TOKEN)] = unlockedWithdrawalsCountSTETH;
        unlockedWithdrawalsCount[lrtConfig.getLSTToken(LRTConstants.ETHX_TOKEN)] = unlockedWithdrawalsCountETHx;
        unlockedWithdrawalsCount[LRTConstants.ETH_TOKEN] = unlockedWithdrawalsCountETH;
    }
```

**File:** contracts/LRTUnstakingVault.sol (L25-30)
```text
contract LRTUnstakingVault is
    ILRTUnstakingVault,
    LRTConfigRoleChecker,
    PausableUpgradeable,
    ReentrancyGuardUpgradeable
{
```

**File:** contracts/LRTConverter.sol (L28-35)
```text
contract LRTConverter is
    ILRTConverter,
    LRTConfigRoleChecker,
    ReentrancyGuardUpgradeable,
    UnstakeSwETH,
    UnstakeStETH,
    IERC721Receiver
{
```
