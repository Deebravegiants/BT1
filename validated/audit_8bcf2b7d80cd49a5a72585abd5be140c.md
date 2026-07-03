### Title
Token Deposits Incur Zero Protocol Fee Due to Uninitialized `tokenFeeBps` Mapping - (File: contracts/pools/RSETHPool.sol)

---

### Summary
`RSETHPool.sol` has two overloaded `viewSwapRsETHAmountAndFee` functions: one for ETH deposits that applies the global `feeBps`, and one for ERC-20 token deposits that reads from `tokenFeeBps[token]`. Because `addSupportedToken` never initialises `tokenFeeBps[token]`, every newly added token defaults to a fee rate of zero. ETH depositors pay the configured fee; token depositors pay nothing. This is the direct structural analog of the Caviar M-10 bug: an inconsistency across deposit paths causes the protocol to collect far less fee than intended.

---

### Finding Description

**ETH deposit path** (`viewSwapRsETHAmountAndFee(uint256 amount)`):

```solidity
fee = amount * feeBps / 10_000;
```

`feeBps` is set at initialisation and is non-zero in production. [1](#0-0) 

**Token deposit path** (`viewSwapRsETHAmountAndFee(uint256 amount, address token)`):

```solidity
uint256 feeBpsForToken = tokenFeeBps[token];
fee = amount * feeBpsForToken / 10_000;
```

`tokenFeeBps[token]` is a Solidity mapping that defaults to `0`. [2](#0-1) 

**Root cause — `addSupportedToken` never writes `tokenFeeBps[token]`:**

```solidity
function addSupportedToken(address token, address oracle, address bridge) external onlyRole(TIMELOCK_ROLE) {
    ...
    supportedTokenList.push(token);
    supportedTokenOracle[token] = oracle;
    tokenBridge[token] = bridge;
    // tokenFeeBps[token] is never set here
    emit AddSupportedToken(token, oracle, bridge);
}
``` [3](#0-2) 

A separate setter exists but is not called during token registration: [4](#0-3) 

The same structural defect is present in every pool variant that supports per-token fees (`RSETHPoolNoWrapper`, `RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`), all of which share the same `viewSwapRsETHAmountAndFee(amount, token)` pattern with `fee = amount * feeBps / 10_000` where `feeBps` is read from the same uninitialised per-token mapping. [5](#0-4) [6](#0-5) [7](#0-6) [8](#0-7) 

---

### Impact Explanation

Every token deposit made before an admin explicitly calls `setTokenFeeBps` yields `fee = 0`. The protocol treasury receives no fee revenue from the token deposit path. This is a permanent loss of unclaimed yield for the protocol on all token volume processed through these pools.

**Impact: High — Theft of unclaimed yield.**

---

### Likelihood Explanation

The default state of any newly added token is `tokenFeeBps[token] == 0`. Any user who calls `deposit(token, amount, referralId)` while this default persists pays zero fee. No special privileges or conditions are required; the path is reachable by any unprivileged depositor. The window lasts from token addition until an admin separately calls `setTokenFeeBps`, which is not enforced or prompted by the contract.

**Likelihood: High** — the zero-fee state is the default and requires no attacker action.

---

### Recommendation

Add a `tokenFeeBps` parameter to `addSupportedToken` (and its equivalents in all pool variants) and write it atomically during token registration:

```solidity
function addSupportedToken(
    address token,
    address oracle,
    address bridge,
    uint256 _feeBps          // <-- add this
) external onlyRole(TIMELOCK_ROLE) {
    if (_feeBps > 10_000) revert InvalidFeeAmount();
    ...
    tokenFeeBps[token] = _feeBps;   // <-- initialise here
    emit AddSupportedToken(token, oracle, bridge);
}
```

This mirrors how `feeBps` is set for ETH at initialisation and eliminates the inconsistency between the two deposit paths.

---

### Proof of Concept

1. Admin calls `addSupportedToken(wstETH, oracle, bridge)` — `tokenFeeBps[wstETH]` is `0`.
2. User calls `deposit(wstETH, 10 ether, "ref")`.
3. `viewSwapRsETHAmountAndFee(10 ether, wstETH)` returns `fee = 10 ether * 0 / 10_000 = 0`.
4. `feeEarnedInToken[wstETH] += 0` — protocol collects nothing.
5. The same user depositing `10 ether` of native ETH via `deposit("ref")` would pay `10 ether * feeBps / 10_000` (e.g., 5 bps → 0.005 ETH).
6. The two paths are inconsistent; all token volume is fee-free until an admin intervenes.

### Citations

**File:** contracts/pools/RSETHPool.sol (L311-312)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
```

**File:** contracts/pools/RSETHPool.sol (L335-336)
```text
        uint256 feeBpsForToken = tokenFeeBps[token];
        fee = amount * feeBpsForToken / 10_000;
```

**File:** contracts/pools/RSETHPool.sol (L583-594)
```text
    function setTokenFeeBps(
        address token,
        uint256 _feeBps
    )
        external
        onlyRole(DEFAULT_ADMIN_ROLE)
        onlySupportedToken(token)
    {
        if (_feeBps > 10_000) revert InvalidFeeAmount();
        tokenFeeBps[token] = _feeBps;
        emit TokenFeeBpsSet(token, _feeBps);
    }
```

**File:** contracts/pools/RSETHPool.sol (L637-656)
```text
    function addSupportedToken(address token, address oracle, address bridge) external onlyRole(TIMELOCK_ROLE) {
        UtilLib.checkNonZeroAddress(token);
        UtilLib.checkNonZeroAddress(oracle);
        UtilLib.checkNonZeroAddress(bridge);

        if (supportedTokenOracle[token] != address(0)) {
            revert AlreadySupportedToken();
        }
        if (tokenBridge[token] != address(0)) {
            revert AlreadySupportedToken();
        }
        if (IOracle(oracle).getRate() == 0) {
            revert UnsupportedOracle();
        }
        supportedTokenList.push(token);
        supportedTokenOracle[token] = oracle;
        tokenBridge[token] = bridge;

        emit AddSupportedToken(token, oracle, bridge);
    }
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L301-302)
```text
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;
```

**File:** contracts/pools/RSETHPoolV3.sol (L324-325)
```text
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L442-443)
```text
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;
```

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L360-361)
```text
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;
```
