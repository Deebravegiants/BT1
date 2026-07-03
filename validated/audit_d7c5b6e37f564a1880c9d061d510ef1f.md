### Title
ETH Deposit Limit Is Never Enforced Due to Missing `+ amount` in Boundary Check - (File: contracts/LRTDepositPool.sol)

### Summary
`_checkIfDepositAmountExceedesCurrentLimit` in `LRTDepositPool.sol` applies a fundamentally broken boundary check for ETH deposits: it omits the incoming deposit `amount` from the comparison, so the `depositLimitByAsset` cap is never actually enforced for ETH. Any unprivileged depositor can push the total ETH held by the protocol arbitrarily above the configured limit.

### Finding Description
The function `_checkIfDepositAmountExceedesCurrentLimit` has two branches — one for ETH and one for ERC-20 tokens:

```solidity
// contracts/LRTDepositPool.sol  lines 676-682
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));   // ← amount never used
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // ← correct
}
```

For ERC-20 assets the check correctly evaluates `totalAssetDeposits + amount > limit`, blocking any deposit that would push the running total past the cap.

For ETH the check evaluates only `totalAssetDeposits > limit`, completely ignoring the incoming `amount`. Two distinct defects are present simultaneously:

1. **Missing `+ amount`** — the new deposit is never added before the comparison, so the check can only ever return `true` when the total has *already* exceeded the limit from a previous deposit. A fresh deposit of any size is always permitted as long as `totalAssetDeposits ≤ limit`.
2. **`>` instead of `>=`** (the direct analog to the reported bug) — even if `amount` were added back, when `totalAssetDeposits == limit` the expression `totalAssetDeposits > limit` evaluates to `false`, allowing one more deposit that pushes the total to `limit + amount`, identical in structure to the `MaxSize > reservedSizeShort` off-by-one in the reference report.

### Impact Explanation
The `depositLimitByAsset` cap for `ETH_TOKEN` is the protocol's primary mechanism for bounding how much ETH is accepted and subsequently staked into EigenLayer. Because the check never includes the incoming `amount`, a depositor can call `depositETH` with an arbitrarily large `msg.value` (subject only to their own balance) and receive rsETH in return, minting rsETH well beyond the intended ceiling. This constitutes unbounded over-issuance of rsETH relative to the protocol's risk parameters, causing the protocol to fail to deliver its promised deposit-limit guarantees and potentially creating downstream insolvency if EigenLayer or other integrated systems cannot absorb the excess.

**Impact**: Low — Contract fails to deliver promised returns (deposit limit guarantee is broken for ETH); with sufficient deposit volume the excess minting could escalate toward protocol insolvency.

### Likelihood Explanation
The entry point `depositETH` is public and payable, requiring no special role. Any ETH holder can trigger the path. The defect is present in every deployment of the current code and requires no precondition beyond the current total being at or below the limit (the normal operating state). Likelihood is **High**.

### Recommendation
Mirror the ERC-20 branch for ETH by including `amount` in the comparison and using `>=` to prevent the off-by-one:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits + amount >= lrtConfig.depositLimitByAsset(asset));
}
```

This aligns the ETH branch with the ERC-20 branch and ensures the limit is enforced before the deposit is accepted.

### Proof of Concept

Assume `depositLimitByAsset[ETH_TOKEN] = 1000 ether` and `totalAssetDeposits(ETH) = 999 ether`.

**Current (broken) behaviour:**
- `_checkIfDepositAmountExceedesCurrentLimit(ETH, 500 ether)`
- evaluates `999 ether > 1000 ether` → `false`
- deposit proceeds; total becomes `1499 ether`, 499 ETH above the cap.

**Expected behaviour:**
- should evaluate `999 + 500 = 1499 ether >= 1000 ether` → `true`
- deposit reverts with `MaximumDepositLimitReached`.

The attacker-controlled path is:
1. Call `LRTDepositPool.depositETH{value: X}(minRSETH, referralId)` with any `X`.
2. `_beforeDeposit` calls `_checkIfDepositAmountExceedesCurrentLimit(ETH_TOKEN, X)`.
3. The ETH branch returns `false` (limit not exceeded) regardless of `X`, so `_mintRsETH` is called and rsETH is issued beyond the cap. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** contracts/LRTDepositPool.sol (L76-93)
```text
    function depositETH(
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        payable
        nonReentrant
        whenNotPaused
        onlySupportedAsset(LRTConstants.ETH_TOKEN)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);

        // interactions
        _mintRsETH(rsethAmountToMint);

        emit ETHDeposit(msg.sender, msg.value, rsethAmountToMint, referralId);
    }
```

**File:** contracts/LRTDepositPool.sol (L648-670)
```text
    function _beforeDeposit(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected
    )
        private
        view
        returns (uint256 rsethAmountToMint)
    {
        if (depositAmount == 0 || depositAmount < minAmountToDeposit) {
            revert InvalidAmountToDeposit();
        }

        if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
            revert MaximumDepositLimitReached();
        }

        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
    }
```

**File:** contracts/LRTDepositPool.sol (L676-682)
```text
    function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
        uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
        if (asset == LRTConstants.ETH_TOKEN) {
            return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));
        }
        return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
    }
```
