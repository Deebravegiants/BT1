### Title
Missing Storage Gap in `LRTConfigRoleChecker` Enables Storage Corruption on Upgrade - (File: contracts/utils/LRTConfigRoleChecker.sol)

### Summary

`LRTConfigRoleChecker` is an abstract contract with a declared state variable (`lrtConfig`) that is inherited by every major upgradeable contract in the protocol. It defines no `__gap` storage reservation. If a future upgrade adds any new state variable to `LRTConfigRoleChecker`, the storage layout of every child contract will be silently shifted, corrupting critical protocol state.

### Finding Description

`LRTConfigRoleChecker` declares one storage variable:

```solidity
// contracts/utils/LRTConfigRoleChecker.sol:13
ILRTConfig public lrtConfig;
``` [1](#0-0) 

No `__gap` array is present anywhere in the file. A grep across the entire `contracts/` tree confirms zero occurrences of `__gap`.

This contract is the shared base for every core upgradeable contract in the protocol:

| Child Contract | Inherits |
|---|---|
| `LRTDepositPool` | `LRTConfigRoleChecker`, `PausableUpgradeable`, `ReentrancyGuardUpgradeable` |
| `NodeDelegator` | `LRTConfigRoleChecker`, `PausableUpgradeable`, `ReentrancyGuardUpgradeable` |
| `RSETH` | `LRTConfigRoleChecker`, `ERC20Upgradeable`, `PausableUpgradeable` |
| `LRTOracle` | `LRTConfigRoleChecker`, `Initializable` |
| `LRTWithdrawalManager` | `LRTConfigRoleChecker`, `PausableUpgradeable`, `ReentrancyGuardUpgradeable` |
| `LRTUnstakingVault` | `LRTConfigRoleChecker`, `PausableUpgradeable`, `ReentrancyGuardUpgradeable` | [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6) 

The inheritance graph (contracts without a gap are marked `[NO GAP]`):

```
LRTDepositPool [has own vars]
  └── LRTConfigRoleChecker [NO GAP, has lrtConfig var]
  └── PausableUpgradeable [has __gap]
  └── ReentrancyGuardUpgradeable [has __gap]

NodeDelegator [has own vars]
  └── LRTConfigRoleChecker [NO GAP, has lrtConfig var]
  └── PausableUpgradeable [has __gap]
  └── ReentrancyGuardUpgradeable [has __gap]

RSETH [has own vars]
  └── LRTConfigRoleChecker [NO GAP, has lrtConfig var]
  └── ERC20Upgradeable [has __gap]
  └── PausableUpgradeable [has __gap]

LRTOracle [has own vars]
  └── LRTConfigRoleChecker [NO GAP, has lrtConfig var]

LRTWithdrawalManager [has own vars]
  └── LRTConfigRoleChecker [NO GAP, has lrtConfig var]
  └── PausableUpgradeable [has __gap]
  └── ReentrancyGuardUpgradeable [has __gap]

LRTUnstakingVault [has own vars]
  └── LRTConfigRoleChecker [NO GAP, has lrtConfig var]
  └── PausableUpgradeable [has __gap]
  └── ReentrancyGuardUpgradeable [has __gap]
```

Because `LRTConfigRoleChecker` occupies the first storage slot(s) in every child contract's layout, adding even one new variable to it during an upgrade would shift all subsequent storage slots by one position. The `__gap` arrays in `PausableUpgradeable` and `ReentrancyGuardUpgradeable` protect those contracts' own future additions, but they do not protect against a shift caused by a parent contract that appears before them in the linearization order.

### Impact Explanation

If a new state variable is added to `LRTConfigRoleChecker` in a future upgrade implementation:

- `LRTDepositPool`: `maxNodeDelegatorLimit`, `minAmountToDeposit`, `isNodeDelegator`, `nodeDelegatorQueue`, `maxNegligibleAmount` all shift by one slot. [8](#0-7) 
- `NodeDelegator`: `eigenPod`, `stakedButUnverifiedNativeETH`, `lastNonce` all shift. [9](#0-8) 
- `RSETH`: `maxMintAmountPerDay`, `currentPeriodMintedAmount`, `periodStartTime`, `custodyAddress`, `transfersBlockedUntil`, `isPermanentlyExempt` all shift. [10](#0-9) 
- `LRTWithdrawalManager`: All withdrawal queue mappings, nonces, and Aave integration state shift. [11](#0-10) 
- `LRTUnstakingVault`: `uncompletedWithdrawalCount`, `maxUncompletedWithdrawalCount`, `queuedWithdrawalsBuffer` shift. [12](#0-11) 

Corrupted storage in any of these contracts can cause: permanent freezing of user funds (deposits, withdrawals, unstaking), incorrect rsETH minting/burning, broken access control, and protocol insolvency.

### Likelihood Explanation

The protocol is actively upgraded (multiple `reinitializer` functions exist across contracts, e.g., `NodeDelegator.initialize2`, `LRTWithdrawalManager.initialize2/3`, `RSETH.reinitialize`). [13](#0-12)  The development team has already demonstrated a pattern of extending contracts with new variables over time. Any future developer adding a new variable to `LRTConfigRoleChecker` (e.g., a new role address, a flag, or a counter) without awareness of this constraint would silently corrupt all six child contracts simultaneously.

### Recommendation

Add a `__gap` storage array to `LRTConfigRoleChecker` to reserve space for future variables:

```solidity
abstract contract LRTConfigRoleChecker {
    ILRTConfig public lrtConfig;

    // Reserve storage slots for future upgrades
    uint256[49] private __gap;

    // ... rest of contract
}
```

The gap size should be chosen so that `lrtConfig` (1 slot) + `__gap` (49 slots) = 50 total slots, matching the OpenZeppelin convention.

### Proof of Concept

1. Deploy `LRTDepositPool` behind a proxy. Observe that `maxNodeDelegatorLimit` is stored at slot 1 (immediately after `lrtConfig` at slot 0).
2. Upgrade `LRTConfigRoleChecker` to add a new `address public newVar` before `lrtConfig` or after it.
3. After the upgrade, reading `maxNodeDelegatorLimit` from the proxy will return the value previously stored at slot 1, which is now interpreted as `newVar`. The actual `maxNodeDelegatorLimit` value is lost, and `nodeDelegatorQueue` and all subsequent mappings are similarly displaced.
4. Any call to `addNodeDelegatorContractToQueue` or `depositETH` will operate on corrupted state, potentially allowing unlimited deposits, broken node delegator tracking, or complete DoS of the deposit/withdrawal system. [1](#0-0) [14](#0-13)

### Citations

**File:** contracts/utils/LRTConfigRoleChecker.sol (L12-13)
```text
abstract contract LRTConfigRoleChecker {
    ILRTConfig public lrtConfig;
```

**File:** contracts/LRTDepositPool.sol (L26-36)
```text
contract LRTDepositPool is ILRTDepositPool, LRTConfigRoleChecker, PausableUpgradeable, ReentrancyGuardUpgradeable {
    using SafeERC20 for IERC20;

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

**File:** contracts/NodeDelegator.sol (L44-56)
```text
    IEigenPod public eigenPod;

    /// @dev Tracks the balance staked to validators and has yet to have the credentials verified with EigenLayer.
    uint256 public stakedButUnverifiedNativeETH;

    /// @dev address of eigenlayer operator to which all restaked funds are delegated to
    /// @dev it is only possible to delegate fully to only one operator per NDC contract
    address private __elOperatorDelegatedTo;

    /// @dev amount of eth expected to receive from extra eth staked for validators
    uint256 private __legacyExtraStakeToReceive;

    uint256 private lastNonce;
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

**File:** contracts/RSETH.sol (L19-32)
```text
    uint256 public maxMintAmountPerDay;

    /// @notice Amount minted in the current 24-hour period
    uint256 public currentPeriodMintedAmount;

    /// @notice Start time of the current 24-hour period
    uint256 public periodStartTime;

    /// @notice Address to which recovered funds are sent
    address public custodyAddress;

    /// @dev If > 0, transfers TO or FROM this address are blocked until timestamp (24h block)
    mapping(address account => uint256 blockedUntil) public transfersBlockedUntil;

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

**File:** contracts/LRTWithdrawalManager.sol (L35-69)
```text
    mapping(address asset => uint256) public minRsEthAmountToWithdraw;
    uint256 public withdrawalDelayBlocks;

    // Next available nonce for withdrawal requests per asset, indicating total requests made.
    mapping(address asset => uint256 nonce) public nextUnusedNonce;

    // Next nonce for which a withdrawal request remains locked.
    mapping(address asset => uint256 requestNonce) public nextLockedNonce;

    // Mapping from a unique request identifier to its corresponding withdrawal request
    mapping(bytes32 requestId => WithdrawalRequest) public withdrawalRequests;

    // Maps each asset to user addresses, pointing to an ordered list of their withdrawal request nonces.
    // Utilizes a double-ended queue for efficient management and removal of initial requests.
    mapping(address asset => mapping(address user => DoubleEndedQueue.Uint256Deque requestNonces)) public
        userAssociatedNonces;

    // Asset amount committed to be withdrawn by users.
    mapping(address asset => uint256 amount) public assetsCommitted;

    mapping(address asset => bool) public isInstantWithdrawalEnabled;
    uint256 public instantWithdrawalFee; // Fee in basis points (1 = 0.01%)

    mapping(address asset => uint256) public unlockedWithdrawalsCount;

    IWrappedTokenGatewayV3 public aaveWETHGateway;
    IAToken public aaveAWETH;
    address public aavePool;
    IPoolDataProvider public aaveDataProvider;
    bool public isAaveIntegrationEnabled;
    uint256 public totalETHDepositedToAave;
    address public constant WETH_ADDRESS = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;

    /// @notice Address that receives instant withdrawal fees. If unset, fees go to the protocol treasury.
    address public instantWithdrawalFeeRecipient;
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

**File:** contracts/LRTUnstakingVault.sol (L36-43)
```text

    mapping(bytes32 => bool) public trackedWithdrawal;

    uint256 public uncompletedWithdrawalCount;
    uint256 public maxUncompletedWithdrawalCount;

    // Portion of the vault reserved for servicing queued withdrawals; unavailable for instant withdrawals.
    mapping(address asset => uint256 buffer) public queuedWithdrawalsBuffer;
```
