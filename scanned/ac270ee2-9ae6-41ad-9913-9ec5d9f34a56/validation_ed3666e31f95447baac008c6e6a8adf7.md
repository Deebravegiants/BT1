### Title
ETH Deposits Permanently Impaired When `LRTConverter.ethValueInWithdrawal()` Reverts - (File: `contracts/LRTDepositPool.sol`)

### Summary
Every ETH deposit into `LRTDepositPool` makes an unguarded external call to `ILRTConverter(lrtConverter).ethValueInWithdrawal()` deep inside the deposit-limit check. If that call reverts for any reason, the entire `depositETH` flow reverts, freezing ETH deposits for all users until the `LRTConverter` issue is resolved or the admin updates the contract address.

### Finding Description
The call chain triggered on every `depositETH` is:

```
depositETH()
  └─ _beforeDeposit()
       └─ _checkIfDepositAmountExceedesCurrentLimit()
            └─ getTotalAssetDeposits(ETH_TOKEN)
                 └─ getAssetDistributionData(ETH_TOKEN)
                      └─ getETHDistributionData()
                           └─ ILRTConverter(lrtConverter).ethValueInWithdrawal()  ← unguarded
```

In `getETHDistributionData`, the `LRTConverter` address is resolved at runtime from `lrtConfig` and called with no try/catch or fallback:

```solidity
address lrtConverter = lrtConfig.getContract(LRTConstants.LRT_CONVERTER);
ethLyingInConverter = ILRTConverter(lrtConverter).ethValueInWithdrawal();
```

If `LRTConverter.ethValueInWithdrawal()` reverts — due to a bug in `LRTConverter`, an unexpected internal state (e.g., during an upgrade window), or a zero-address misconfiguration — the revert propagates all the way up through `_beforeDeposit`, causing `depositETH` to revert for every caller. There is no mechanism to bypass or skip this call.

The same call chain is also triggered by `depositAsset` for the ETH asset path, and by `getAssetCurrentLimit`, making the impact broader than just `depositETH`.

### Impact Explanation
**Medium — Temporary freezing of funds.**

All ETH deposits are blocked for every user until either:
1. The bug in `LRTConverter` is fixed and the contract is redeployed, or
2. An admin updates the `LRT_CONVERTER` address in `lrtConfig`.

During this window, users cannot enter the protocol with ETH. Funds already in the protocol are not at direct theft risk, but new capital is frozen out and existing users cannot add to their positions.

### Likelihood Explanation
`LRTConverter` is a separate upgradeable protocol contract. Any revert path inside `ethValueInWithdrawal()` — including arithmetic errors, unexpected zero-state during an upgrade, or a storage layout collision after a proxy upgrade — propagates directly to `depositETH`. The `LRTConverter` contract is called on every single ETH deposit, so even a transient failure window (e.g., between an upgrade `initialize` call and full re-configuration) would block all deposits. This is a realistic operational risk, not a theoretical one.

### Recommendation
Wrap the external call in a try/catch and fall back to zero (or a cached value) if it reverts:

```solidity
try ILRTConverter(lrtConverter).ethValueInWithdrawal() returns (uint256 val) {
    ethLyingInConverter = val;
} catch {
    ethLyingInConverter = 0; // conservative: under-counts TVL, never blocks deposits
}
```

This mirrors the pattern already used in `LRTWithdrawalManager` for the Aave integration (`try this.depositToAaveExternal(...) { } catch { ... }`), making the deposit path resilient to transient failures in downstream protocol contracts.

### Proof of Concept

1. `LRTConverter` is upgraded or enters a broken state where `ethValueInWithdrawal()` reverts.
2. Any user calls `LRTDepositPool.depositETH{value: 1 ether}(0, "")`.
3. Execution reaches `getETHDistributionData()` at line 499 of `LRTDepositPool.sol`.
4. `ILRTConverter(lrtConverter).ethValueInWithdrawal()` reverts.
5. The revert bubbles up through `getAssetDistributionData` → `getTotalAssetDeposits` → `_checkIfDepositAmountExceedesCurrentLimit` → `_beforeDeposit` → `depositETH`.
6. The user's deposit fails. Every subsequent ETH deposit fails identically.
7. No user-accessible path exists to bypass this check; only an admin can fix it by updating `lrtConfig`. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

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

**File:** contracts/LRTDepositPool.sol (L467-500)
```text
    function getETHDistributionData()
        public
        view
        override
        returns (
            uint256 ethLyingInDepositPool,
            uint256 ethLyingInNDCs,
            uint256 ethStakedInEigenLayer,
            uint256 ethUnstakingFromEigenLayer,
            uint256 ethLyingInConverter,
            uint256 ethLyingInUnstakingVault
        )
    {
        ethLyingInDepositPool = address(this).balance;

        uint256 ndcsCount = nodeDelegatorQueue.length;

        for (uint256 i; i < ndcsCount;) {
            ethLyingInNDCs += nodeDelegatorQueue[i].balance;

            ethStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getEffectivePodShares();
            ethUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i])
                .getAssetUnstaking(LRTConstants.ETH_TOKEN);
            unchecked {
                ++i;
            }
        }

        address lrtUnstakingVault = lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT);
        ethLyingInUnstakingVault = lrtUnstakingVault.balance;

        address lrtConverter = lrtConfig.getContract(LRTConstants.LRT_CONVERTER);
        ethLyingInConverter = ILRTConverter(lrtConverter).ethValueInWithdrawal();
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

**File:** contracts/LRTWithdrawalManager.sol (L310-317)
```text
        if (isAaveIntegrationEnabled && asset == LRTConstants.ETH_TOKEN && assetAmountUnlocked > 0) {
            try this.depositToAaveExternal(assetAmountUnlocked) { }
            catch (bytes memory reason) {
                emit AaveDepositFailed(assetAmountUnlocked, reason);
                // Silently fail if Aave deposit fails (e.g., pool at max capacity)
                // Funds remain in contract for withdrawals
            }
        }
```
