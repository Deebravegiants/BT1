### Title
Missing Deposit Amount in ETH Deposit Limit Check Allows Deposits Beyond Protocol Cap - (File: `contracts/LRTDepositPool.sol`)

---

### Summary

The `_checkIfDepositAmountExceedesCurrentLimit` function in `LRTDepositPool.sol` applies an asymmetric limit check: for ERC20 assets it correctly includes the incoming deposit amount in the comparison, but for ETH it omits the deposit amount entirely. This mirrors the exact class of bug in the reference report — a missing value component in a cost/limit accounting function — and allows any depositor to push the protocol's ETH holdings past the configured deposit cap.

---

### Finding Description

`_checkIfDepositAmountExceedesCurrentLimit` is the sole gate that enforces the per-asset deposit limit before rsETH is minted: [1](#0-0) 

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));   // ← amount ignored
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // ← amount included
}
```

For every ERC20 asset the prospective deposit (`amount`) is added to the running total before comparing against the cap. For ETH the `amount` parameter is silently discarded; only the pre-deposit total is tested. Consequently, whenever `totalAssetDeposits == depositLimit` the check returns `false` (limit not exceeded) and the deposit proceeds, even though `totalAssetDeposits + msg.value` will exceed the limit after the call completes.

The check is invoked unconditionally inside `_beforeDeposit`, which is called by the public `depositETH` entry point: [2](#0-1) [3](#0-2) 

---

### Impact Explanation

The deposit limit (`depositLimitByAsset`) is the protocol's primary TVL risk-management control for ETH. Exceeding it means:

1. More ETH is accepted and rsETH is minted against it than the protocol intends to back.
2. The surplus ETH may not be deployable into EigenLayer strategies (which have their own caps), leaving it idle and diluting yield for all rsETH holders.
3. The protocol's accounting invariant — that total ETH deposits never exceed the configured cap — is broken, which can affect downstream oracle pricing and withdrawal queue sizing.

**Impact rating: Low** — the protocol fails to deliver its promised deposit-cap guarantee; no direct fund theft occurs, but the risk management boundary is silently violated.

---

### Likelihood Explanation

- The entry point `depositETH` is public and payable; any externally-owned account can call it.
- The bug is triggered whenever `totalAssetDeposits` is at or near `depositLimitByAsset(ETH_TOKEN)`, a condition that occurs naturally as the protocol fills up.
- No special permissions, flash loans, or oracle manipulation are required.
- **Likelihood: Medium** — the condition is reached in normal protocol operation.

---

### Recommendation

Add the incoming `amount` to the ETH branch of the check, matching the ERC20 branch:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

---

### Proof of Concept

1. Admin sets `depositLimitByAsset(ETH_TOKEN) = 1000 ether`.
2. Protocol accumulates `totalAssetDeposits(ETH_TOKEN) = 1000 ether` (exactly at the cap).
3. Attacker calls `depositETH{value: 100 ether}(0, "")`.
4. `_checkIfDepositAmountExceedesCurrentLimit(ETH_TOKEN, 100 ether)` evaluates `1000 ether > 1000 ether` → `false` → limit not exceeded.
5. `_mintRsETH` mints rsETH for the attacker; the protocol now holds 1100 ETH against a 1000 ETH cap.
6. The deposit limit is bypassed with no revert, and the attacker receives rsETH backed by ETH the protocol was not supposed to accept. [1](#0-0)

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
