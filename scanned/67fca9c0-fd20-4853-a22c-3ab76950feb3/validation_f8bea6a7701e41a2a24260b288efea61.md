### Title
`startTimestamp` Bypass via Uninitialized Default Zero Value Allows Premature Deposits — (`contracts/pools/RSETHPoolV3.sol`, `RSETHPoolV3ExternalBridge.sol`, `RSETHPoolV3WithNativeChainBridge.sol`, `RSETHPoolV2.sol`)

---

### Summary

The `limitDailyMint` modifier in all four L2 pool variants contains a start-time guard that is silently bypassed whenever `startTimestamp` holds its default value of `0`. Because `startTimestamp` is a `uint256`, the check `block.timestamp < startTimestamp` evaluates to `block.timestamp < 0`, which is always `false` in Solidity. Any depositor can therefore call `deposit()` and mint `wrsETH` before the protocol's intended launch window, as long as `dailyMintLimit` is non-zero.

---

### Finding Description

Every pool variant stores a `startTimestamp` that is meant to gate when deposits are accepted:

```solidity
// RSETHPoolV3.sol – limitDailyMint modifier
if (block.timestamp < startTimestamp) {
    revert MintBeforeStartTimestamp();
}
``` [1](#0-0) 

`startTimestamp` is only written inside the `reinitialize(uint256 _dailyMintLimit, uint256 _startTimestamp)` function, which is a one-shot `reinitializer(N)`:

```solidity
if (block.timestamp > _startTimestamp) {
    revert InvalidStartTimestamp();
}
dailyMintLimit = _dailyMintLimit;
startTimestamp = _startTimestamp;
``` [2](#0-1) 

A separate admin function `setDailyMintLimit()` can set `dailyMintLimit` to a non-zero value at any time **without touching `startTimestamp`**:

```solidity
function setDailyMintLimit(uint256 _dailyMintLimit) external onlyRole(DEFAULT_ADMIN_ROLE) {
    if (_dailyMintLimit == 0) { revert InvalidDailyMintLimit(); }
    dailyMintLimit = _dailyMintLimit;
    ...
}
``` [3](#0-2) 

If `setDailyMintLimit()` is called before `reinitialize(dailyMintLimit, startTimestamp)` is executed (e.g., during an upgrade transition window), the contract reaches a state where `startTimestamp == 0` and `dailyMintLimit > 0`. In that state:

- `block.timestamp < 0` → always `false` → the guard never fires
- `getCurrentDay()` returns `block.timestamp / 1 days` ≈ 19,900 (days since Unix epoch), which is always greater than `lastMintDay`'s initial value of `0`, so `dailyMintAmount` is reset to `0` on the first call [4](#0-3) 

The same pattern is present identically in:
- `RSETHPoolV3ExternalBridge.sol` lines 130–131 [5](#0-4) 
- `RSETHPoolV3WithNativeChainBridge.sol` lines 108–111 [6](#0-5) 
- `RSETHPoolV2.sol` lines 72–75 [7](#0-6) 

---

### Impact Explanation

Any unprivileged depositor can call `deposit()` and receive `wrsETH` before the protocol's intended launch time. The daily mint limit is also rendered ineffective for the first deposit window because `getCurrentDay()` returns a large Unix-epoch-relative value that always exceeds `lastMintDay == 0`, resetting the daily accumulator on every call until `lastMintDay` is updated. The protocol fails to deliver its promised controlled-launch guarantee. No direct fund theft occurs.

**Impact: Low — Contract fails to deliver promised returns, but doesn't lose value.**

---

### Likelihood Explanation

The trigger requires `startTimestamp == 0` and `dailyMintLimit > 0` simultaneously. This arises when:

1. An admin calls `setDailyMintLimit()` before the `reinitialize(dailyMintLimit, startTimestamp)` upgrade step is executed — a realistic race condition during multi-step upgrade deployments.
2. A new pool variant is deployed where `reinitialize` has not yet been called but `setDailyMintLimit()` has been called as a standalone configuration step.

The upgrade history of `RSETHPoolV3ExternalBridge` (reinitializers 1–6) shows that `startTimestamp` was introduced at reinitializer(4), meaning any contract still at version ≤3 that has `setDailyMintLimit()` called on it is immediately vulnerable. [8](#0-7) 

---

### Recommendation

Replace the unguarded default-zero bypass with an explicit check that also rejects the uninitialized state:

```solidity
modifier limitDailyMint(uint256 amount, address token) {
    // Reject if startTimestamp has never been set OR if we are before it
    if (startTimestamp == 0 || block.timestamp < startTimestamp) {
        revert MintBeforeStartTimestamp();
    }
    ...
}
```

Apply this fix to all four pool contracts: `RSETHPoolV3.sol`, `RSETHPoolV3ExternalBridge.sol`, `RSETHPoolV3WithNativeChainBridge.sol`, and `RSETHPoolV2.sol`.

---

### Proof of Concept

```solidity
// Scenario: reinitialize(dailyMintLimit, startTimestamp) has NOT been called yet.
// Admin calls setDailyMintLimit() to configure the pool.
pool.setDailyMintLimit(100 ether);          // startTimestamp remains 0

// Attacker deposits immediately — no start time has been set
pool.deposit{value: 1 ether}("ref");        // succeeds: block.timestamp < 0 is false

// wrsETH is minted to attacker before the intended launch window
assert(wrsETH.balanceOf(attacker) > 0);
```

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L96-99)
```text
    modifier limitDailyMint(uint256 amount, address token) {
        if (block.timestamp < startTimestamp) {
            revert MintBeforeStartTimestamp();
        }
```

**File:** contracts/pools/RSETHPoolV3.sol (L191-197)
```text
        // startTimestamp cannot be in the past
        if (block.timestamp > _startTimestamp) {
            revert InvalidStartTimestamp();
        }

        dailyMintLimit = _dailyMintLimit;
        startTimestamp = _startTimestamp;
```

**File:** contracts/pools/RSETHPoolV3.sol (L339-341)
```text
    function getCurrentDay() public view returns (uint256) {
        return (block.timestamp - startTimestamp) / 1 days;
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L605-611)
```text
    function setDailyMintLimit(uint256 _dailyMintLimit) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (_dailyMintLimit == 0) {
            revert InvalidDailyMintLimit();
        }
        dailyMintLimit = _dailyMintLimit;
        emit DailyMintLimitSet(_dailyMintLimit);
    }
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L130-133)
```text
    modifier limitDailyMint(uint256 amount, address token) {
        if (block.timestamp < startTimestamp) {
            revert MintBeforeStartTimestamp();
        }
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L224-235)
```text
    /**
     * @dev Version history:
     * - reinitializer(1): Initial deployment and setup of the contract with initial roles, wrsETH token, fees and
     * oracles. Only native ETH deposits used to be supported.
     * - reinitializer(2): Added support for ETH bridging via Stargate from L2 to L1.
     * - reinitializer(3): Upgraded to update the LayerZero V2 chain ID for the ETH mainnet.
     * - reinitializer(4): Introduced daily minting limit functionality to control the amount of wrsETH that can
     * be minted per day.
     * - reinitializer(5): Added a new supported token (wstETH), along with the oracle and the native bridging logic for
     * it.
     * - reinitializer(6): This upgrade enables native bridging of ETH from L2 to L1.
     */
```

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L108-111)
```text
    modifier limitDailyMint(uint256 amount, address token) {
        if (block.timestamp < startTimestamp) {
            revert MintBeforeStartTimestamp();
        }
```

**File:** contracts/pools/RSETHPoolV2.sol (L72-75)
```text
    modifier limitDailyMint(uint256 amount) {
        if (block.timestamp < startTimestamp) {
            revert MintBeforeStartTimestamp();
        }
```
