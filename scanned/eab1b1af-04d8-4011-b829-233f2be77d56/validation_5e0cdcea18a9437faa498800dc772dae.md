### Title
Access-Controlled `pause()` Cannot Be Called Via Forced Inclusion When L2 Sequencer Is Down - (File: `contracts/pools/RSETHPool.sol`, `contracts/pools/RSETHPoolV2.sol`, `contracts/pools/RSETHPoolV3.sol`, `contracts/pools/RSETHPoolNoWrapper.sol`)

---

### Summary

All L2 pool contracts in the LRT-rsETH protocol (`RSETHPool`, `RSETHPoolV2`, `RSETHPoolV3`, `RSETHPoolNoWrapper`) are deployed on rollup chains (Arbitrum, Unichain, Optimism-stack chains). Their access control modifiers — inherited from OpenZeppelin's `AccessControlUpgradeable` — check only `msg.sender` against the granted role. They do not check the **aliased** sender address that rollups like Arbitrum and Optimism apply when a transaction is force-included from L1. As a result, when the L2 sequencer is down, the admin/pauser cannot execute emergency functions (most critically `pause()`) via forced inclusion, leaving the protocol unprotectable during an active exploit.

---

### Finding Description

Each L2 pool contract defines a `pause()` function gated by `onlyRole(PAUSER_ROLE)`:

- `RSETHPool.pause()` — `onlyRole(PAUSER_ROLE)` [1](#0-0) 
- `RSETHPoolV2.pause()` — `onlyRole(PAUSER_ROLE)` [2](#0-1) 
- `RSETHPoolV3.pause()` — `onlyRole(PAUSER_ROLE)` [3](#0-2) 
- `RSETHPoolNoWrapper.pause()` — `onlyRole(PAUSER_ROLE)` [4](#0-3) 

The `onlyRole` modifier is inherited from OpenZeppelin's `AccessControlUpgradeable` and resolves to a `hasRole(role, msg.sender)` check. It does not consider the aliased address. On Arbitrum and Optimism, when an L1 contract (or EOA) submits a transaction via the delayed inbox / forced inclusion path, the `msg.sender` seen on L2 is `originalAddress + 0x1111000000000000000000000000000000001111`. Because the aliased address is never granted `PAUSER_ROLE` or `DEFAULT_ADMIN_ROLE`, every access-controlled call submitted via forced inclusion will revert.

The same applies to all other admin-only functions: `unpause()`, `setDailyMintLimit()`, `setFeeBps()`, `setIsEthDepositEnabled()`, `reinitialize()`, etc. [5](#0-4) [6](#0-5) 

---

### Impact Explanation

**Medium — Temporary freezing of funds.**

When the L2 sequencer is down, user deposits (ETH and supported tokens) held in the pool cannot be protected by pausing the contract. If an exploit is active simultaneously, the attacker can drain the pool via forced inclusion while the admin is unable to respond in kind. The `deposit()` functions are public and callable by anyone (including via forced inclusion), so an attacker is not blocked, but the admin is. [7](#0-6) [8](#0-7) 

---

### Likelihood Explanation

**Low-to-Medium.** Arbitrum and Unichain (both explicitly named in the codebase) support forced inclusion. Sequencer downtime events have occurred historically. An attacker who discovers an exploit in the pool's swap logic (e.g., oracle manipulation) could wait for or force a sequencer outage and then execute the exploit via forced inclusion while the admin is locked out of `pause()`. [9](#0-8) [10](#0-9) 

---

### Recommendation

In each L2 pool contract, update the `pause()` (and other critical admin functions) to also accept the aliased equivalent of the privileged address. Concretely, add a check of the form:

```solidity
address aliased = address(uint160(msg.sender) - uint160(0x1111000000000000000000000000000000001111));
```

and verify that `aliased` holds the required role, in addition to the standard `msg.sender` check. Alternatively, grant the aliased address the `PAUSER_ROLE` and `DEFAULT_ADMIN_ROLE` at initialization time for each L2 deployment.

---

### Proof of Concept

1. `RSETHPool` is deployed on Arbitrum. The admin holds `PAUSER_ROLE` at address `A`.
2. The Arbitrum sequencer goes offline; forced inclusion via the L1 delayed inbox is the only transaction path.
3. An attacker identifies a price oracle manipulation in `viewSwapRsETHAmountAndFee` and submits a `deposit()` call via forced inclusion — this succeeds because `deposit()` has no role restriction.
4. The admin attempts to call `pause()` via forced inclusion from L1. On L2, `msg.sender` is `A + 0x1111...1111`, which does not hold `PAUSER_ROLE`. The call reverts.
5. The attacker continues draining the pool until the sequencer recovers or funds are exhausted. [1](#0-0) [7](#0-6)

### Citations

**File:** contracts/pools/RSETHPool.sol (L30-35)
```text
/// @title RSETHPool
/// @notice This contract is the pool contract for the rsETH pool on *Arbitrum*
/// @dev it differs from other RSETHPool contracts in other chains as it uses LZ_RSETH as the canonical rsETH token of
/// the chain.
/// @dev it was the first RSETHPool contract to be deployed in an L2 hence the legacy variables
contract RSETHPool is ERC20Upgradeable, AccessControlUpgradeable, ReentrancyGuardUpgradeable {
```

**File:** contracts/pools/RSETHPool.sol (L85-93)
```text
    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");

    /// @dev Mapping of token to fee basis points
    mapping(address token => uint256 feeBps) public tokenFeeBps;

    modifier whenNotPaused() {
        if (paused) revert ContractPaused();
        _;
    }
```

**File:** contracts/pools/RSETHPool.sol (L265-278)
```text
    function deposit(string memory referralId) external payable nonReentrant whenNotPaused {
        if (!isEthDepositEnabled) revert EthDepositDisabled();
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        IERC20(address(wrsETH)).safeTransfer(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }
```

**File:** contracts/pools/RSETHPool.sol (L737-740)
```text
    function pause() external onlyRole(PAUSER_ROLE) whenNotPaused {
        paused = true;
        emit Paused(msg.sender);
    }
```

**File:** contracts/pools/RSETHPoolV2.sol (L344-347)
```text
    function pause() external onlyRole(PAUSER_ROLE) whenNotPaused {
        paused = true;
        emit Paused(msg.sender);
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L63-74)
```text
    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");

    /// @notice The timelock role identifier
    bytes32 public constant TIMELOCK_ROLE = keccak256("TIMELOCK_ROLE");

    /// @notice The operator role identifier
    bytes32 public constant OPERATOR_ROLE = keccak256("OPERATOR_ROLE");

    modifier whenNotPaused() {
        if (paused) revert ContractPaused();
        _;
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L246-265)
```text
    function deposit(string memory referralId)
        external
        payable
        nonReentrant
        whenNotPaused
        limitDailyMint(msg.value, ETH_IDENTIFIER)
    {
        if (!isEthDepositEnabled) revert EthDepositDisabled();
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L592-595)
```text
    function pause() external onlyRole(PAUSER_ROLE) whenNotPaused {
        paused = true;
        emit Paused(msg.sender);
    }
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L27-30)
```text
/// @title RSETHPoolNoWrapper
/// @notice This contract is the deposit pool for the chains where there is no rsETH wrapper contract (e.g. Arbitrum,
/// Unichain)
contract RSETHPoolNoWrapper is AccessControlUpgradeable, PausableUpgradeable, ReentrancyGuardUpgradeable {
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L673-675)
```text
    function pause() external onlyRole(PAUSER_ROLE) whenNotPaused {
        _pause();
    }
```
