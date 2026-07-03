### Title
Wrong Inequality in ETH Deposit Limit Check Allows Limit Bypass - (File: contracts/LRTDepositPool.sol)

### Summary
`_checkIfDepositAmountExceedesCurrentLimit()` in `LRTDepositPool.sol` uses an asymmetric inequality for ETH vs. LST assets. The ETH branch omits the incoming deposit `amount` from the comparison, allowing ETH deposits to exceed the configured deposit cap while LST deposits are correctly bounded.

### Finding Description

In `LRTDepositPool._checkIfDepositAmountExceedesCurrentLimit()`:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset)); // missing `+ amount`
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

For LSTs the check is `totalAssetDeposits + amount > depositLimit` — correctly accounting for the incoming deposit. For ETH the check is `totalAssetDeposits > depositLimit` — the incoming `amount` is never added. This means:

- When `totalAssetDeposits == depositLimit`, the ETH check returns `false` (not exceeded), so the deposit proceeds even though the cap is already fully consumed.
- When `totalAssetDeposits < depositLimit` but `totalAssetDeposits + amount > depositLimit`, the ETH check still returns `false`, allowing a single deposit to push total ETH deposits arbitrarily far above the cap.

The LST path would correctly return `true` and revert in both cases.

### Impact Explanation

Any ETH depositor can call `depositETH()` and mint rsETH even after the ETH deposit cap has been reached, or with an amount that would push total deposits well beyond the cap. The deposit limit is a protocol-level safety invariant (e.g., to bound EigenLayer strategy exposure). Bypassing it means the protocol accepts more ETH than intended and mints more rsETH than the cap was designed to allow.

**Impact: Low** — Contract fails to deliver its promised deposit-limit invariant for ETH, but no direct fund theft or loss of value occurs from a single transaction.

### Likelihood Explanation

Any unprivileged ETH depositor can trigger this. No special role, front-running, or external dependency is required. The condition is reachable whenever `totalAssetDeposits >= depositLimit - amount` for any non-zero ETH deposit.

### Recommendation

Add `amount` to the ETH branch comparison, mirroring the LST branch:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

### Proof of Concept

1. Admin sets `depositLimitByAsset(ETH_TOKEN) = 1000 ether`.
2. Protocol accumulates `totalAssetDeposits(ETH) = 1000 ether` (limit exactly reached).
3. `getAssetCurrentLimit(ETH)` returns `0` — limit is consumed.
4. User calls `depositETH{value: 500 ether}(minRSETH, "")`.
5. `_checkIfDepositAmountExceedesCurrentLimit(ETH, 500 ether)` evaluates `1000 ether > 1000 ether` → `false` → deposit is **not** blocked.
6. 500 ETH is accepted and rsETH is minted, pushing total ETH deposits to 1500 ether — 50% above the cap.
7. For any LST with the same state, step 5 would evaluate `1000 ether + 500 ether > 1000 ether` → `true` → deposit correctly reverts with `MaximumDepositLimitReached`. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

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

**File:** contracts/LRTDepositPool.sol (L402-409)
```text
    function getAssetCurrentLimit(address asset) public view override returns (uint256) {
        uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
        if (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset)) {
            return 0;
        }

        return lrtConfig.depositLimitByAsset(asset) - totalAssetDeposits;
    }
```

**File:** contracts/LRTDepositPool.sol (L648-669)
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
