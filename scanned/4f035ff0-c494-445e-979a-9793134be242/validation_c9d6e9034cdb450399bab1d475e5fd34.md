### Title
`setFeeBps()` Uses Inconsistent Upper Bound `1000` Instead of `10_000`, Permanently Blocking Fee Configuration Above 10% — (`contracts/pools/RSETHPoolV3.sol`, `contracts/pools/RSETHPoolV3WithNativeChainBridge.sol`)

---

### Summary

`RSETHPoolV3.setFeeBps()` and `RSETHPoolV3WithNativeChainBridge.setFeeBps()` enforce an upper bound of `1000` on the fee basis points parameter, while the fee arithmetic throughout both contracts divides by `10_000`. Every other pool contract in the codebase uses `> 10_000` as the guard. The mismatch permanently prevents the admin from setting any fee above 10 % (1 000 bps) in these two contracts, even though the denominator and the rest of the protocol treat 10 000 as the full-scale value.

---

### Finding Description

Both affected contracts compute fees identically to every other pool:

```solidity
// RSETHPoolV3.sol L300, L324
fee = amount * feeBps / 10_000;
```

Yet their `setFeeBps` guards use `1000` instead of `10_000`:

```solidity
// RSETHPoolV3.sol L519
function setFeeBps(uint256 _feeBps) external onlyRole(DEFAULT_ADMIN_ROLE) {
    if (_feeBps > 1000) revert InvalidFeeAmount();   // ← 1 000, not 10 000
    feeBps = _feeBps;
    emit FeeBpsSet(_feeBps);
}
```

```solidity
// RSETHPoolV3WithNativeChainBridge.sol L582
function setFeeBps(uint256 _feeBps) external onlyRole(DEFAULT_ADMIN_ROLE) {
    if (_feeBps > 1000) revert InvalidFeeAmount();   // ← 1 000, not 10 000
    feeBps = _feeBps;
    emit FeeBpsSet(_feeBps);
}
```

Every other pool in the repository uses the correct bound:

| Contract | Guard |
|---|---|
| `RSETHPool` | `> 10_000` |
| `RSETHPoolNoWrapper` | `> 10_000` |
| `RSETHPoolV2` | `> 10_000` |
| `RSETHPoolV2NBA` | `> 10_000` |
| `RSETHPoolV3ExternalBridge` | `> 10_000` |
| `AGETHPoolV3` | `> 10_000` |
| **`RSETHPoolV3`** | **`> 1_000` ← wrong** |
| **`RSETHPoolV3WithNativeChainBridge`** | **`> 1_000` ← wrong** |

The denominator `10_000` represents 100 % in basis-point arithmetic. The guard `> 1000` therefore silently caps the maximum settable fee at 10 %, making any call with `_feeBps` in the range `[1001, 10_000]` revert with `InvalidFeeAmount`, even though those values are semantically valid.

---

### Impact Explanation

**Low — Contract fails to deliver promised returns, but doesn't lose value.**

The admin role in `RSETHPoolV3` and `RSETHPoolV3WithNativeChainBridge` is permanently unable to configure a fee above 10 % (1 000 bps). Any governance or operational decision that requires a fee in the range 1 001–10 000 bps will always revert, silently locking the fee configuration below the intended ceiling. Because the denominator is `10_000`, a fee of, say, 2 000 bps (20 %) is a valid protocol concept but is unreachable in these two contracts. The protocol cannot deliver the full fee-configuration range it is designed to support.

---

### Likelihood Explanation

**Medium.** The bug is triggered the moment the admin attempts to set a fee above 10 % in either contract. Given that the protocol operates across multiple L2 chains and may need to adjust fees in response to market conditions, the probability of hitting this ceiling is non-trivial. The inconsistency with every other pool contract makes it likely to be encountered during routine operations.

---

### Recommendation

Change the guard in both contracts from `1000` to `10_000` to match the fee denominator and the rest of the codebase:

```solidity
// RSETHPoolV3.sol and RSETHPoolV3WithNativeChainBridge.sol
function setFeeBps(uint256 _feeBps) external onlyRole(DEFAULT_ADMIN_ROLE) {
-   if (_feeBps > 1000) revert InvalidFeeAmount();
+   if (_feeBps > 10_000) revert InvalidFeeAmount();
    feeBps = _feeBps;
    emit FeeBpsSet(_feeBps);
}
```

---

### Proof of Concept

1. Deploy `RSETHPoolV3` (or `RSETHPoolV3WithNativeChainBridge`) and call `initialize` with any valid parameters.
2. As `DEFAULT_ADMIN_ROLE`, call `setFeeBps(1001)` — this represents a 10.01 % fee, which is a valid basis-point value given the `10_000` denominator.
3. The call reverts with `InvalidFeeAmount` even though `1001 / 10_000 = 0.1001` is a perfectly valid fee ratio.
4. Call `setFeeBps(1000)` — succeeds.
5. Call `setFeeBps(5000)` (50 % fee, valid in every other pool) — reverts.
6. Repeat on `RSETHPoolV3WithNativeChainBridge` — identical behaviour.

The same call succeeds on `RSETHPoolV3ExternalBridge.setFeeBps(5000)` because that contract correctly uses `> 10_000`. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L299-301)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;
```

**File:** contracts/pools/RSETHPoolV3.sol (L518-522)
```text
    function setFeeBps(uint256 _feeBps) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (_feeBps > 1000) revert InvalidFeeAmount();
        feeBps = _feeBps;
        emit FeeBpsSet(_feeBps);
    }
```

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L581-585)
```text
    function setFeeBps(uint256 _feeBps) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (_feeBps > 1000) revert InvalidFeeAmount();
        feeBps = _feeBps;
        emit FeeBpsSet(_feeBps);
    }
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L744-748)
```text
    function setFeeBps(uint256 _feeBps) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (_feeBps > 10_000) revert InvalidFeeAmount();
        feeBps = _feeBps;
        emit FeeBpsSet(_feeBps);
    }
```

**File:** contracts/pools/RSETHPool.sol (L574-578)
```text
    function setFeeBps(uint256 _feeBps) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (_feeBps > 10_000) revert InvalidFeeAmount();
        feeBps = _feeBps;
        emit FeeBpsSet(_feeBps);
    }
```
