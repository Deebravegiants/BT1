### Title
ETH Deposit Limit Bypass Due to Missing Amount in Limit Check - (File: contracts/LRTDepositPool.sol)

### Summary
`LRTDepositPool._checkIfDepositAmountExceedesCurrentLimit()` applies an asymmetric validation: for ERC20 assets it correctly checks `totalAssetDeposits + amount > limit`, but for native ETH it only checks `totalAssetDeposits > limit`, omitting the incoming `amount`. Any depositor can therefore push ETH deposits arbitrarily beyond the configured `depositLimitByAsset` cap in a single transaction.

### Finding Description
The function at the heart of the deposit guard is:

```solidity
// contracts/LRTDepositPool.sol lines 676-682
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));   // ← amount not included
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // ← correct for ERC20
}
``` [1](#0-0) 

This function is called from `_beforeDeposit`, which gates both `depositETH` and `depositAsset`:

```solidity
if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
    revert MaximumDepositLimitReached();
}
``` [2](#0-1) 

Because the ETH branch evaluates `totalAssetDeposits > limit` (strict greater-than, without adding `amount`), the check returns `false` — i.e., "limit not exceeded" — whenever the current total is at or below the limit, regardless of how large the incoming deposit is. A depositor who calls `depositETH` while `totalAssetDeposits == limit - 1 wei` can send any amount of ETH and the guard will not revert.

The deposit limit is set per-asset in `LRTConfig.depositLimitByAsset` and is the sole on-chain mechanism preventing over-exposure of ETH to EigenLayer strategies. [3](#0-2) 

### Impact Explanation
The ETH deposit cap configured by the protocol is rendered ineffective. Any unprivileged depositor can mint rsETH against an arbitrarily large ETH deposit in a single call, pushing the protocol's total ETH exposure in EigenLayer far beyond the intended limit. This constitutes a contract failing to deliver its promised invariant (the deposit cap) without direct loss of user funds.

**Impact: Low — Contract fails to deliver promised returns, but doesn't lose value.**

### Likelihood Explanation
The entry path is `depositETH()`, a public payable function with no access control. The condition to trigger the bypass is simply that `getTotalAssetDeposits(ETH_TOKEN) <= depositLimitByAsset(ETH_TOKEN)` at the time of the call — a condition that is true for the entire operational lifetime of the protocol until the limit is already breached. No flash loan, no multi-step sequence, and no special role is required.

**Likelihood: High.**

### Recommendation
Add `amount` to the ETH branch, mirroring the ERC20 branch:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    // Unified check: include the incoming amount for both ETH and ERC20
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

### Proof of Concept

1. Admin sets `depositLimitByAsset[ETH_TOKEN] = 100 ether`.
2. Legitimate users deposit until `getTotalAssetDeposits(ETH_TOKEN) == 99 ether`.
3. Attacker calls `depositETH{value: 10_000 ether}(0, "")`.
4. Inside `_checkIfDepositAmountExceedesCurrentLimit`: `totalAssetDeposits (99 ether) > limit (100 ether)` → `false` → no revert.
5. `_mintRsETH` mints rsETH for 10 000 ETH; total ETH in protocol becomes 10 099 ETH — 100× the intended cap.
6. All 10 099 ETH will eventually be forwarded to EigenLayer via `NodeDelegator`, far exceeding the risk limit the admin intended to enforce. [4](#0-3) [5](#0-4)

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

**File:** contracts/LRTConfig.sol (L23-23)
```text
    mapping(address token => uint256 amount) public depositLimitByAsset;
```
