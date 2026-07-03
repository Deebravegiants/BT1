### Title
ETH Deposit Limit Bypass Due to Missing Current Amount in Cap Check - (File: contracts/LRTDepositPool.sol)

### Summary
`_checkIfDepositAmountExceedesCurrentLimit` in `LRTDepositPool` applies an asymmetric check for ETH vs. ERC20 assets. The ETH branch omits the incoming deposit amount from the comparison, allowing any single ETH deposit to bypass the configured `depositLimitByAsset` cap entirely.

### Finding Description
In `contracts/LRTDepositPool.sol`, the function `_checkIfDepositAmountExceedesCurrentLimit` has two branches:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset)); // ← amount NOT included
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // ← correct
}
```

For ERC20 LSTs the check is `totalAssetDeposits + amount > depositLimit` — correct. For ETH the check is `totalAssetDeposits > depositLimit` — the incoming `amount` (`msg.value`) is never added. The function therefore returns `false` (no limit exceeded) for any ETH deposit as long as the pre-existing total has not already surpassed the limit, regardless of how large the new deposit is. [1](#0-0) 

The ETH deposit entry point `depositETH` calls `_beforeDeposit`, which calls `_checkIfDepositAmountExceedesCurrentLimit`, so every ETH deposit goes through this flawed gate. [2](#0-1) 

The deposit limit is stored per-asset in `LRTConfig.depositLimitByAsset` and is intended to cap total protocol exposure. [3](#0-2) 

### Impact Explanation
**Low — Contract fails to deliver promised returns.**

The protocol configures `depositLimitByAsset[ETH_TOKEN]` as a hard cap on total ETH exposure. Because the incoming deposit amount is excluded from the ETH branch of the limit check, a single depositor can push total ETH deposits arbitrarily above the configured cap in one transaction. The cap is rendered meaningless for ETH. No funds are directly stolen, but the protocol invariant that limits ETH exposure to EigenLayer is violated, and more rsETH is minted than the cap was designed to allow.

### Likelihood Explanation
High. Any unprivileged user calling `depositETH` with `msg.value` large enough to exceed the remaining cap will succeed without revert, as long as `getTotalAssetDeposits(ETH_TOKEN)` has not already crossed the limit before their call. No special role, front-running, or multi-transaction setup is required.

### Recommendation
Add `amount` to the ETH branch, mirroring the ERC20 branch:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
``` [4](#0-3) 

### Proof of Concept
1. Admin sets `depositLimitByAsset[ETH_TOKEN] = 100 ether`.
2. Protocol accumulates `totalAssetDeposits(ETH) = 99 ether` through normal usage.
3. Attacker calls `depositETH{value: 10_000 ether}(0, "")`.
4. Inside `_checkIfDepositAmountExceedesCurrentLimit`: `totalAssetDeposits (99e18) > depositLimit (100e18)` → `false` → no revert.
5. `_mintRsETH` mints rsETH for 10 000 ETH. Total ETH in protocol is now 10 099 ETH, 100× the intended cap. [5](#0-4)

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
