### Title
Missing `__gap` in `LRTConfigRoleChecker` Base Contract Enables Storage Collision on Upgrade - (File: `contracts/utils/LRTConfigRoleChecker.sol`)

---

### Summary

`LRTConfigRoleChecker` is an abstract base contract inherited by every major upgradeable protocol contract. It defines `lrtConfig` at storage slot 0 but contains no `__gap` reservation. Any future addition of a state variable to `LRTConfigRoleChecker` during an upgrade will shift the storage layout of all inheriting contracts, corrupting critical state variables across the entire protocol.

---

### Finding Description

`LRTConfigRoleChecker` declares one storage variable and no `__gap`:

```solidity
abstract contract LRTConfigRoleChecker {
    ILRTConfig public lrtConfig;   // slot 0
    // NO __gap
}
``` [1](#0-0) 

This contract is the first parent in the inheritance chain of every major upgradeable contract in the protocol:

- `LRTDepositPool is ILRTDepositPool, LRTConfigRoleChecker, PausableUpgradeable, ReentrancyGuardUpgradeable`
- `NodeDelegator is INodeDelegator, LRTConfigRoleChecker, PausableUpgradeable, ReentrancyGuardUpgradeable`
- `LRTWithdrawalManager is ILRTWithdrawalManager, LRTConfigRoleChecker, PausableUpgradeable, ReentrancyGuardUpgradeable`
- `LRTUnstakingVault is ILRTUnstakingVault, LRTConfigRoleChecker, PausableUpgradeable, ReentrancyGuardUpgradeable`
- `RSETH is Initializable, LRTConfigRoleChecker, ERC20Upgradeable, PausableUpgradeable`
- `LRTOracle is ILRTOracle, LRTConfigRoleChecker, Initializable`
- `PubkeyRegistry is IPubkeyRegistry, LRTConfigRoleChecker, Initializable`
- `LRTConverter is ILRTConverter, LRTConfigRoleChecker, ReentrancyGuardUpgradeable, ...` [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) 

The OpenZeppelin upgradeable contracts in the chain (`PausableUpgradeable`, `ReentrancyGuardUpgradeable`, `ERC20Upgradeable`, `AccessControlUpgradeable`) all include `__gap` arrays to protect their own storage regions. However, `LRTConfigRoleChecker` — which sits at the very beginning of the storage layout — has no such protection.

The concrete contracts themselves also declare no `__gap`, meaning they cannot safely serve as base contracts for future versioned implementations either.

The protocol has already demonstrated active upgrade activity: `RSETH` uses `reinitializer(2)`, confirming that upgrades are performed in production. [6](#0-5) 

---

### Impact Explanation

**Severity: Critical — Permanent freezing of funds / Direct theft of user funds**

If a developer adds any new state variable to `LRTConfigRoleChecker` and upgrades any inheriting contract, the new implementation's storage layout diverges from the proxy's existing storage. Concretely, for `LRTDepositPool`:

| Slot | Before upgrade | After upgrade (new var added to `LRTConfigRoleChecker`) |
|------|---------------|----------------------------------------------------------|
| 0 | `lrtConfig` | `lrtConfig` |
| 1 | `_paused` (PausableUpgradeable) | **new variable** (reads `_paused`'s raw value) |
| 2 | `_status` (ReentrancyGuard, after gap) | `_paused` (shifted) |
| … | `maxNodeDelegatorLimit` | shifted by 1 |

Consequences:
- `lrtConfig` read from wrong slot → all `onlyLRTAdmin`, `onlyLRTManager`, `onlyLRTOperator` modifiers return wrong results → unauthorized callers can invoke privileged functions → **direct theft of deposited assets**
- `_paused` corrupted → contract cannot be paused in an emergency, or is permanently paused → **permanent freezing of user funds**
- `maxNodeDelegatorLimit`, `minAmountToDeposit`, `nodeDelegatorQueue` corrupted → deposit/withdrawal accounting broken → **protocol insolvency**

The same corruption applies to `RSETH` (minting/burning controls), `LRTWithdrawalManager` (withdrawal queue), and `LRTUnstakingVault` (unstaking logic).

---

### Likelihood Explanation

- The protocol is under active development and has already performed at least one upgrade (`RSETH` `reinitializer(2)`).
- `LRTConfigRoleChecker` is a shared base contract that developers may reasonably extend (e.g., adding a new role or a cached address) without realizing the storage impact.
- No `__gap` exists anywhere in the production `contracts/` directory — confirmed by the absence of any `__gap` declaration in any file under `contracts/`.
- The vulnerability is latent and silent: it will not manifest until the next upgrade that modifies `LRTConfigRoleChecker`, at which point the damage is irreversible without a full migration.

---

### Recommendation

1. Add a `__gap` to `LRTConfigRoleChecker` immediately:
   ```solidity
   abstract contract LRTConfigRoleChecker {
       ILRTConfig public lrtConfig;
       uint256[49] private __gap; // reserve 49 slots for future variables
   }
   ```
2. Add `__gap` arrays to all concrete upgradeable contracts (`LRTDepositPool`, `NodeDelegator`, `LRTWithdrawalManager`, `LRTUnstakingVault`, `RSETH`, `LRTOracle`, `LRTConverter`, `PubkeyRegistry`, `FeeReceiver`, `L1Vault`, `L1VaultV2`, `RsETHTokenWrapper`, `KernelMerkleDistributor`, `KernelTop100MerkleDistributor`).
3. Establish a pre-upgrade checklist that verifies storage layout compatibility using tools such as OpenZeppelin's `hardhat-upgrades` plugin or `slither`'s storage layout checker.
4. Leave comments next to all state variables indicating their storage slot numbers.

---

### Proof of Concept

**Step 1 — Current storage layout of `LRTDepositPool` proxy (simplified):**
```
Slot 0:   lrtConfig                    ← LRTConfigRoleChecker
Slot 1:   _paused                      ← PausableUpgradeable
Slot 2–50: __gap[49]                   ← PausableUpgradeable gap
Slot 51:  _status                      ← ReentrancyGuardUpgradeable
Slot 52–100: __gap[49]                 ← ReentrancyGuardUpgradeable gap
Slot 101: maxNodeDelegatorLimit        ← LRTDepositPool
Slot 102: minAmountToDeposit           ← LRTDepositPool
Slot 103: isNodeDelegator (mapping)    ← LRTDepositPool
```

**Step 2 — Developer adds `address public newRoleAddress` to `LRTConfigRoleChecker` and upgrades `LRTDepositPool`:**

New implementation storage layout:
```
Slot 0:   lrtConfig                    ← LRTConfigRoleChecker
Slot 1:   newRoleAddress               ← LRTConfigRoleChecker (NEW)
Slot 2:   _paused                      ← PausableUpgradeable (SHIFTED)
Slot 3–51: __gap[49]                   ← PausableUpgradeable gap (SHIFTED)
Slot 52:  _status                      ← ReentrancyGuardUpgradeable (SHIFTED)
Slot 53–101: __gap[49]                 ← ReentrancyGuardUpgradeable gap (SHIFTED)
Slot 102: maxNodeDelegatorLimit        ← LRTDepositPool (SHIFTED)
```

**Step 3 — Proxy storage is unchanged; new implementation reads:**
- Slot 1 as `newRoleAddress` → actually contains the old `_paused` value (e.g., `1` = paused) → `newRoleAddress` = `address(1)`
- Slot 2 as `_paused` → actually contains old `__gap[0]` (zero) → contract appears unpaused even if it was paused
- Slot 102 as `maxNodeDelegatorLimit` → actually contains old `minAmountToDeposit` value → wrong limit enforced

**Step 4 — Attacker observes corrupted `lrtConfig` (if slot 0 is also affected in a multi-variable addition) or exploits broken role checks to call `addNodeDelegatorContractToQueue` with a malicious NDC, draining deposited assets.** [1](#0-0) [7](#0-6) [8](#0-7)

### Citations

**File:** contracts/utils/LRTConfigRoleChecker.sol (L12-14)
```text
abstract contract LRTConfigRoleChecker {
    ILRTConfig public lrtConfig;

```

**File:** contracts/LRTDepositPool.sol (L26-51)
```text
contract LRTDepositPool is ILRTDepositPool, LRTConfigRoleChecker, PausableUpgradeable, ReentrancyGuardUpgradeable {
    using SafeERC20 for IERC20;

    uint256 public maxNodeDelegatorLimit;
    uint256 public minAmountToDeposit;

    mapping(address => uint256) public isNodeDelegator; // 0: not a node delegator, 1: is a node delegator
    address[] public nodeDelegatorQueue;

    /// @notice maximum amount that can be ignored
    uint256 public maxNegligibleAmount;

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    /// @dev Initializes the contract
    /// @param lrtConfigAddr LRT config address
    function initialize(address lrtConfigAddr) external initializer {
        UtilLib.checkNonZeroAddress(lrtConfigAddr);
        __Pausable_init();
        __ReentrancyGuard_init();
        maxNodeDelegatorLimit = 10;
        lrtConfig = ILRTConfig(lrtConfigAddr);
        emit UpdatedLRTConfig(lrtConfigAddr);
```

**File:** contracts/NodeDelegator.sol (L39-39)
```text
contract NodeDelegator is INodeDelegator, LRTConfigRoleChecker, PausableUpgradeable, ReentrancyGuardUpgradeable {
```

**File:** contracts/RSETH.sol (L13-13)
```text
contract RSETH is Initializable, LRTConfigRoleChecker, ERC20Upgradeable, PausableUpgradeable {
```

**File:** contracts/RSETH.sol (L109-117)
```text
    function reinitialize(uint256 _periodStartTime, address _custodyAddress) external reinitializer(2) onlyLRTManager {
        if (_periodStartTime > block.timestamp || _periodStartTime <= block.timestamp - 1 days) {
            revert PeriodStartTimeShouldBeWithin24Hours();
        }
        periodStartTime = _periodStartTime;
        emit PeriodStartTimeSet(_periodStartTime);

        _setCustodyAddress(_custodyAddress);
    }
```

**File:** contracts/LRTOracle.sol (L23-23)
```text
contract LRTOracle is ILRTOracle, LRTConfigRoleChecker, Initializable {
```
