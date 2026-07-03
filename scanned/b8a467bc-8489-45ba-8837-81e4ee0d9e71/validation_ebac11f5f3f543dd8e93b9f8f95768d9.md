### Title
Inconsistent `feeBps` Maximum Cap Across L2 Pool Contracts Allows Up to 100% Fee in `RSETHPoolV3ExternalBridge` — (File: contracts/pools/RSETHPoolV3ExternalBridge.sol)

### Summary
The maximum allowed `feeBps` is enforced at two different thresholds across the protocol's L2 pool contracts with no single source of truth. `RSETHPoolV3ExternalBridge` and `RSETHPool` permit fees up to 10,000 bps (100%), while `RSETHPoolV3` and `RSETHPoolV3WithNativeChainBridge` cap fees at 1,000 bps (10%). This structural inconsistency means the same parameter is governed by different limits depending on which pool variant is deployed, directly mirroring the OVM mismatch pattern.

### Finding Description
`RSETHPoolV3ExternalBridge.setFeeBps` enforces:

```solidity
if (_feeBps > 10_000) revert InvalidFeeAmount();
``` [1](#0-0) 

While `RSETHPoolV3.setFeeBps` and `RSETHPoolV3WithNativeChainBridge.setFeeBps` enforce:

```solidity
if (_feeBps > 1000) revert InvalidFeeAmount();
``` [2](#0-1) [3](#0-2) 

`RSETHPool` and `RSETHPoolNoWrapper` also use the 10,000 bps cap: [4](#0-3) [5](#0-4) 

The `feeBps` value is consumed directly in `viewSwapRsETHAmountAndFee` for both ETH and token deposits:

```solidity
fee = amount * feeBps / 10_000;
uint256 amountAfterFee = amount - fee;
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
``` [6](#0-5) 

At `feeBps = 10_000`, `amountAfterFee = 0` and `rsETHAmount = 0` — the depositor's entire input is consumed as fees and they receive nothing. At `feeBps = 5_000`, users receive half the rsETH they are entitled to. There is no on-chain enforcement preventing `feeBps` from being set to any value up to 10,000 in `RSETHPoolV3ExternalBridge`, while the same value would be rejected in `RSETHPoolV3`.

### Impact Explanation
Users depositing ETH or LSTs through `RSETHPoolV3ExternalBridge` (deployed on chains such as Base/Optimism) are exposed to a fee cap 10× higher than users on chains using `RSETHPoolV3`. A misconfigured `feeBps` between 1,001 and 10,000 bps causes depositors to receive materially less rsETH than the protocol promises, with the extreme case (10,000 bps) resulting in zero rsETH returned for a full deposit. This is a direct failure to deliver promised returns and, at the extreme, constitutes complete loss of deposited funds for affected users.

**Impact: Low — Contract fails to deliver promised returns** (with potential escalation to Critical at `feeBps = 10_000`).

### Likelihood Explanation
The inconsistency is structural: an operator configuring fees across multiple deployed pool variants may apply a value (e.g., 5,000 bps) that is silently accepted by `RSETHPoolV3ExternalBridge` but would revert in `RSETHPoolV3`. Because there is no shared constant or registry enforcing a uniform cap, the mismatch can arise from a routine configuration update without any malicious intent — exactly the misconfiguration scenario the external report describes. The protocol deploys multiple pool variants across many L2s, increasing the surface area for this divergence.

### Recommendation
Define a single protocol-wide constant for the maximum fee basis points and reference it in every pool contract's `setFeeBps` function. For example:

```solidity
uint256 public constant MAX_FEE_BPS = 1000; // 10%
```

Alternatively, store the cap in a shared registry (e.g., `LRTConfig`) so that all pool variants read from one authoritative source, eliminating the possibility of per-contract divergence.

### Proof of Concept
1. Admin calls `RSETHPoolV3ExternalBridge.setFeeBps(5000)` → **succeeds** (5000 ≤ 10,000).
2. Admin calls `RSETHPoolV3.setFeeBps(5000)` → **reverts** with `InvalidFeeAmount` (5000 > 1000).
3. A user deposits 1 ETH through `RSETHPoolV3ExternalBridge`:
   - `fee = 1e18 * 5000 / 10_000 = 0.5e18`
   - `amountAfterFee = 0.5e18`
   - User receives rsETH worth only 0.5 ETH — 50% of their deposit silently taken as fees.
4. The same deposit through `RSETHPoolV3` would be protected by the 10% cap, yielding rsETH worth ≥ 0.9 ETH.

The two contracts enforce the same parameter (`feeBps`) with different limits and no programmatic cross-check, directly mirroring the OVM gas-limit mismatch pattern.

### Citations

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L418-427)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
    }
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L744-747)
```text
    function setFeeBps(uint256 _feeBps) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (_feeBps > 10_000) revert InvalidFeeAmount();
        feeBps = _feeBps;
        emit FeeBpsSet(_feeBps);
```

**File:** contracts/pools/RSETHPoolV3.sol (L518-521)
```text
    function setFeeBps(uint256 _feeBps) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (_feeBps > 1000) revert InvalidFeeAmount();
        feeBps = _feeBps;
        emit FeeBpsSet(_feeBps);
```

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L581-584)
```text
    function setFeeBps(uint256 _feeBps) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (_feeBps > 1000) revert InvalidFeeAmount();
        feeBps = _feeBps;
        emit FeeBpsSet(_feeBps);
```

**File:** contracts/pools/RSETHPool.sol (L574-577)
```text
    function setFeeBps(uint256 _feeBps) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (_feeBps > 10_000) revert InvalidFeeAmount();
        feeBps = _feeBps;
        emit FeeBpsSet(_feeBps);
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L524-528)
```text
    function setFeeBps(uint256 _feeBps) external onlyRole(TIMELOCK_ROLE) {
        if (_feeBps > 10_000) revert InvalidFeeAmount();

        feeBps = _feeBps;

```
