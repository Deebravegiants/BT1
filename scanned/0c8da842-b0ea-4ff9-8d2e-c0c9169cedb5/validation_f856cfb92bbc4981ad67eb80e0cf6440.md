### Title
ETH Deposit Limit Check Missing Deposit Amount Allows Bypassing Configured Cap - (`contracts/LRTDepositPool.sol`)

### Summary
`LRTDepositPool._checkIfDepositAmountExceedesCurrentLimit` uses an incorrect condition for ETH: it omits the incoming deposit amount from the comparison, so any ETH deposit passes the limit check as long as the running total has not already exceeded the cap. Any unprivileged depositor can exploit this to push ETH deposits arbitrarily beyond the configured limit.

### Finding Description
In `LRTDepositPool._checkIfDepositAmountExceedesCurrentLimit`, the ETH branch and the ERC-20 branch apply structurally different checks:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));   // ← missing `+ amount`
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
``` [1](#0-0) 

For every ERC-20 asset the function correctly evaluates `totalAssetDeposits + amount > limit`. For ETH it evaluates only `totalAssetDeposits > limit`, ignoring the size of the incoming deposit entirely. The function returns `false` (i.e., "limit not exceeded") whenever the running total has not yet crossed the cap, regardless of how large the new deposit is. The caller `_beforeDeposit` then proceeds to mint rsETH for the full deposit amount. [2](#0-1) 

The public entry point `depositETH` calls `_beforeDeposit` with no additional limit guard, so the flawed check is the only gate. [3](#0-2) 

The analogous view helper `getAssetCurrentLimit` correctly subtracts `totalAssetDeposits` from the cap, confirming the intended semantics is `totalAssetDeposits + amount ≤ limit`. [4](#0-3) 

### Impact Explanation
The ETH deposit cap (`depositLimitByAsset[ETH_TOKEN]`) is a risk-management parameter set by governance. Because the check is wrong, a single depositor can send a deposit that is many multiples of the remaining headroom and the transaction will succeed. The protocol will mint rsETH for the full amount, accept the ETH, and record a total that exceeds the configured limit. This violates the protocol's own invariant and can push more ETH into EigenLayer strategies than they are sized to absorb, causing the contract to fail to deliver its promised deposit-limit guarantee.

**Impact: Low** — Contract fails to deliver promised returns (deposit cap is not enforced for ETH); no direct fund theft or permanent freeze, but the risk-management invariant is broken for every ETH depositor.

### Likelihood Explanation
**Likelihood: High** — `depositETH` is a public, permissionless function. No special role or precondition is required. Any depositor who observes that `totalAssetDeposits < depositLimitByAsset[ETH_TOKEN]` can send a deposit of arbitrary size and bypass the cap in a single transaction. The condition is deterministically reachable whenever the ETH deposit limit has not already been exceeded.

### Recommendation
Add the deposit amount to the ETH branch, mirroring the ERC-20 branch:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    // Unified check: include `amount` for both ETH and ERC-20
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

### Proof of Concept
Assume `depositLimitByAsset[ETH_TOKEN] = 100 ether` and `getTotalAssetDeposits(ETH_TOKEN) = 99 ether`.

1. Attacker calls `depositETH{value: 1000 ether}(minRSETH, "")`.
2. `_beforeDeposit` calls `_checkIfDepositAmountExceedesCurrentLimit(ETH_TOKEN, 1000 ether)`.
3. ETH branch evaluates `99 ether > 100 ether` → `false` → limit not exceeded.
4. `_beforeDeposit` returns the rsETH amount for 1000 ETH; `_mintRsETH` mints it.
5. `getTotalAssetDeposits(ETH_TOKEN)` is now 1099 ether — 10× the configured cap — with no revert. [1](#0-0)

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
