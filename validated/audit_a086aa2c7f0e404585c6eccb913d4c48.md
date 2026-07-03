### Title
ETH Deposit Limit Check Omits Deposit Amount, Allowing Any Depositor to Exceed the Configured Cap - (File: contracts/LRTDepositPool.sol)

---

### Summary
`_checkIfDepositAmountExceedesCurrentLimit` applies an asymmetric arithmetic check for ETH versus ERC-20 assets. The ETH branch tests only whether the *current* total already exceeds the limit, without adding the incoming deposit amount. Any unprivileged depositor can therefore push the ETH TVL above the protocol-configured cap in a single transaction.

---

### Finding Description
`LRTDepositPool._checkIfDepositAmountExceedesCurrentLimit` contains two distinct code paths:

```solidity
// contracts/LRTDepositPool.sol  lines 676-682
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset)); // ← amount NOT included
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // ← amount included
}
``` [1](#0-0) 

For every ERC-20 asset the prospective deposit `amount` is added to `totalAssetDeposits` before comparing against the limit, which is the correct guard. For ETH the `amount` parameter is silently ignored. The check therefore only blocks a deposit when the limit has *already* been exceeded in a prior transaction; it never blocks the transaction that first crosses the boundary.

The check is invoked unconditionally inside `_beforeDeposit`, which is called by the public `depositETH` entry point: [2](#0-1) 

---

### Impact Explanation
The ETH deposit cap (`depositLimitByAsset[ETH_TOKEN]`) is a protocol risk-management parameter. When `totalAssetDeposits == limit`, the check returns `false` (no revert) and the deposit is accepted, pushing the on-chain ETH TVL above the intended ceiling. After that single bypass transaction, `totalAssetDeposits > limit` becomes true and all subsequent ETH deposits are blocked, but the excess ETH has already been accepted and rsETH has already been minted against it. The protocol therefore holds more ETH exposure than its own configuration permits.

**Impact class**: Low — Contract fails to deliver promised returns (deposit cap not enforced for ETH), but no direct loss of user funds occurs.

---

### Likelihood Explanation
The condition is reachable by any unprivileged ETH depositor with no preconditions beyond the ETH deposit being enabled and the current total being at or near the configured limit. No special role, front-running, or oracle manipulation is required. Likelihood is **High**.

---

### Recommendation
Add the incoming `amount` to the ETH branch, mirroring the ERC-20 logic:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

---

### Proof of Concept

1. Admin sets `depositLimitByAsset[ETH_TOKEN] = 1000 ether`.
2. Protocol accumulates exactly `1000 ether` of ETH TVL across all NodeDelegators and the DepositPool.
3. Attacker calls `depositETH{value: 500 ether}(0, "")`.
4. Inside `_checkIfDepositAmountExceedesCurrentLimit`:
   - `totalAssetDeposits = 1000 ether`
   - ETH branch: `return (1000 ether > 1000 ether)` → `return false` → no revert.
5. `_mintRsETH` mints rsETH for 500 ETH; the protocol now holds 1500 ETH against a 1000 ETH cap.
6. All subsequent `depositETH` calls revert (`1500 > 1000`), but the 500 ETH excess is permanently accepted. [3](#0-2) [1](#0-0)

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
