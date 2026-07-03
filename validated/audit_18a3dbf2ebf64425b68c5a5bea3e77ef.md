### Title
Unvalidated `feeBps` in `initialize()` Bypasses the Cap Enforced by `setFeeBps()`, Causing Depositors to Receive Fewer wrsETH Than Entitled - (File: contracts/pools/RSETHPoolV3.sol)

### Summary
Every pool `initialize()` function accepts `_feeBps` with no upper-bound check, while the post-deployment `setFeeBps()` setter enforces a strict cap (1 000 bps = 10 % in `RSETHPoolV3` and `RSETHPoolV3WithNativeChainBridge`; 10 000 bps in the remaining pools). A deployment that accidentally supplies an out-of-range `_feeBps` silently over-charges every depositor from block 0, accumulating the excess in `feeEarnedInETH` / `feeEarnedInToken` with no on-chain mechanism to refund affected users.

### Finding Description
`RSETHPoolV3.initialize()` stores `_feeBps` without any guard:

```solidity
// contracts/pools/RSETHPoolV3.sol  lines 207-232
function initialize(
    address admin, address bridger,
    address _wrsETH, uint256 _feeBps,
    address _rsETHOracle, bool _isEthDepositEnabled
) external initializer {
    UtilLib.checkNonZeroAddress(_wrsETH);
    UtilLib.checkNonZeroAddress(_rsETHOracle);
    // ← no check on _feeBps
    ...
    feeBps = _feeBps;          // line 229
    ...
}
```

The post-deployment setter, however, enforces a hard cap:

```solidity
// contracts/pools/RSETHPoolV3.sol  lines 518-522
function setFeeBps(uint256 _feeBps) external onlyRole(DEFAULT_ADMIN_ROLE) {
    if (_feeBps > 1000) revert InvalidFeeAmount();   // max 10 %
    feeBps = _feeBps;
}
```

The same pattern exists in every other pool variant:

| Contract | `initialize()` cap | `setFeeBps()` cap |
|---|---|---|
| `RSETHPoolV3WithNativeChainBridge` | none | 1 000 bps |
| `RSETHPoolV3ExternalBridge` | none | 10 000 bps |
| `RSETHPoolV2` / `RSETHPoolV2ExternalBridge` / `RSETHPoolV2NBA` | none | 10 000 bps |
| `RSETHPool` | none | 10 000 bps |
| `RSETHPoolNoWrapper` | none | 10 000 bps |
| `AGETHPoolV3` | none | 10 000 bps |

The fee is applied to every deposit:

```solidity
// contracts/pools/RSETHPoolV3.sol  lines 299-308
function viewSwapRsETHAmountAndFee(uint256 amount)
    public view returns (uint256 rsETHAmount, uint256 fee)
{
    fee = amount * feeBps / 10_000;
    uint256 amountAfterFee = amount - fee;
    rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
}
```

If `feeBps` is initialised at, say, 5 000 (50 %), every depositor immediately loses half their ETH to fees. The excess accumulates in `feeEarnedInETH` and is extractable by the BRIDGER via `withdrawFees()`. There is no on-chain path to return those fees to the depositors who were over-charged before the error is noticed and corrected.

This is the direct analog of the reference finding: a critical numeric parameter is accepted without the same validation that the post-deployment setter enforces, leading to incorrect accounting that harms users.

### Impact Explanation
Every `deposit()` call made while `feeBps` exceeds the intended cap silently transfers value from depositors to the fee pool. Depositors receive fewer wrsETH/rsETH than the protocol promises. The over-collected fees are irrecoverable by the affected users even after the admin corrects `feeBps` via `setFeeBps()`. Impact: **contract fails to deliver promised returns** (Low); escalates toward **temporary freezing / theft of yield** if the misconfiguration persists across many deposits.

### Likelihood Explanation
Deployment scripts and constructor arguments are human-authored. The inconsistency between the initialization path (no cap) and the setter path (hard cap) creates a latent misconfiguration risk. Because the error is silent—no revert, no event distinguishing an abnormal fee—it may go undetected until users or monitoring tools notice reduced wrsETH output. Likelihood: **Low** (requires a deployment-time mistake), but the absence of any guard makes it structurally possible.

### Recommendation
Apply the same upper-bound check inside every `initialize()` function that is already present in the corresponding `setFeeBps()`:

```solidity
function initialize(..., uint256 _feeBps, ...) external initializer {
    if (_feeBps > 1000) revert InvalidF