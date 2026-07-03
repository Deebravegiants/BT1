### Title
`RsETHTokenWrapper.withdraw()` and `withdrawTo()` Cannot Be Paused While Pool Deposits Can - (File: `contracts/L2/RsETHTokenWrapper.sol`)

### Summary
The `RsETHTokenWrapper` contract has no pause mechanism whatsoever, while every L2 pool contract in the same system (`RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`, `RSETHPoolNoWrapper`) implements a `PAUSER_ROLE`-gated `pause()` function and guards user-facing `deposit()` functions with `whenNotPaused`. This creates an asymmetry: the protocol can halt new `wrsETH` minting but cannot halt the reverse path — users burning `wrsETH` to reclaim the underlying `altRsETH` tokens.

### Finding Description
`RsETHTokenWrapper` does not inherit from any pausable base and exposes four unrestricted, externally callable functions:

- `deposit(address asset, uint256 _amount)` — deposits `altRsETH`, mints `wrsETH`
- `depositTo(address asset, address _to, uint256 _amount)` — same, to a third party
- `withdraw(address asset, uint256 _amount)` — burns `wrsETH`, returns `altRsETH`
- `withdrawTo(address asset, address _to, uint256 _amount)` — same, to a third party

None of these carry any pause guard. The internal `_withdraw` logic burns the caller's `wrsETH` and transfers `altRsETH` 1:1 with no access control beyond the `allowedTokens` check.

In contrast, every pool contract that mints `wrsETH` on behalf of depositors has an explicit `PAUSER_ROLE`, a `pause()` function, and `whenNotPaused` on its `deposit()` entry points. The `RSETHPoolNoWrapper` contract even uses OpenZeppelin's `PausableUpgradeable` directly.

### Impact Explanation
When the protocol activates its emergency pause (e.g., in response to an oracle manipulation, bridge exploit, or regulatory requirement), it can stop new `wrsETH` from being minted via the pool contracts, but it cannot stop any holder from calling `RsETHTokenWrapper.withdraw()` or `withdrawTo()` to burn `wrsETH` and drain the wrapper's `altRsETH` reserves. The protocol fails to deliver its promised ability to fully halt user-facing token flows in an emergency. **Impact: Low — contract fails to deliver promised emergency controls; no direct value loss under normal conditions, but the invariant that "pausing stops all user-facing flows" is broken.**

### Likelihood Explanation
The presence of `PAUSER_ROLE`, `pause()`, and `whenNotPaused` across every pool contract demonstrates a deliberate design intent to be able to halt user interactions. The omission in `RsETHTokenWrapper` is an oversight that will be triggered any time the protocol operator attempts a full emergency pause. Likelihood is **medium** — the pause path is exercised whenever an incident occurs, and the gap will be discovered at the worst possible moment.

### Recommendation
Inherit from `PausableUpgradeable` (or an equivalent) in `RsETHTokenWrapper`, add a `PAUSER_ROLE`-gated `pause()` / `unpause()` pair, and apply `whenNotPaused` to `deposit`, `depositTo`, `withdraw`, and `withdrawTo`. This mirrors the pattern already used in `RSETHPoolNoWrapper`.

### Proof of Concept
1. Protocol detects an exploit and calls `pause()` on all pool contracts — new `wrsETH` minting stops.
2. Attacker (or any user) holds `wrsETH` and calls `RsETHTokenWrapper.withdraw(altRsETH, amount)`.
3. `_withdraw` executes: `_burn(msg.sender, amount)` then `ERC20Upgradeable(altRsETH).safeTransfer(_to, amount)` — no pause check exists, call succeeds.
4. The wrapper's `altRsETH` balance is reduced; the protocol cannot prevent this outflow despite the system being in a paused state.

Relevant code:

`RsETHTokenWrapper` — no `PausableUpgradeable`, no `whenNotPaused` on any user function: [1](#0-0) [2](#0-1) [3](#0-2) 

`RSETHPoolNoWrapper` — same ecosystem, full `PausableUpgradeable` + `whenNotPaused` on `deposit`: [4](#0-3) [5](#0-4) [6](#0-5) 

`RSETHPoolV3` — `PAUSER_ROLE` + `whenNotPaused` on deposits, demonstrating the intended pattern: [7](#0-6) [8](#0-7) [9](#0-8)

### Citations

**File:** contracts/L2/RsETHTokenWrapper.sol (L20-20)
```text
contract RsETHTokenWrapper is Initializable, AccessControlUpgradeable, ERC20Upgradeable, ERC20PermitUpgradeable {
```

**File:** contracts/L2/RsETHTokenWrapper.sol (L84-94)
```text
    function withdraw(address asset, uint256 _amount) external {
        _withdraw(asset, msg.sender, _amount);
    }

    /// @dev Withdraw altRsETH tokens from wrsETH to a user
    /// @param asset The address of the token to withdraw
    /// @param _to The user to withdraw to
    /// @param _amount The amount of tokens to withdraw
    function withdrawTo(address asset, address _to, uint256 _amount) external {
        _withdraw(asset, _to, _amount);
    }
```

**File:** contracts/L2/RsETHTokenWrapper.sol (L120-128)
```text
    function _withdraw(address _asset, address _to, uint256 _amount) internal {
        if (!allowedTokens[_asset]) revert TokenNotAllowed();

        _burn(msg.sender, _amount);

        ERC20Upgradeable(_asset).safeTransfer(_to, _amount);

        emit Withdraw(_asset, msg.sender, _to, _amount);
    }
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L30-30)
```text
contract RSETHPoolNoWrapper is AccessControlUpgradeable, PausableUpgradeable, ReentrancyGuardUpgradeable {
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L231-231)
```text
    function deposit(string memory referralId) external payable nonReentrant whenNotPaused {
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L673-675)
```text
    function pause() external onlyRole(PAUSER_ROLE) whenNotPaused {
        _pause();
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

**File:** contracts/pools/RSETHPoolV3.sol (L246-251)
```text
    function deposit(string memory referralId)
        external
        payable
        nonReentrant
        whenNotPaused
        limitDailyMint(msg.value, ETH_IDENTIFIER)
```

**File:** contracts/pools/RSETHPoolV3.sol (L592-595)
```text
    function pause() external onlyRole(PAUSER_ROLE) whenNotPaused {
        paused = true;
        emit Paused(msg.sender);
    }
```
