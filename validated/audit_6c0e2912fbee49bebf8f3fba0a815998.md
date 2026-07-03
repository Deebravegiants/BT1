### Title
ETH Deposit DOS via Balance Inflation - (File: `contracts/LRTDepositPool.sol`)

### Summary
An unprivileged attacker can send ETH directly to `LRTDepositPool` via its open `receive()` function to inflate `address(this).balance`. Because `getETHDistributionData` counts `address(this).balance` as protocol TVL, this inflated balance can push `getTotalAssetDeposits(ETH)` above the configured deposit limit, causing all subsequent `depositETH` calls to revert with `MaximumDepositLimitReached`, temporarily freezing ETH deposits for all users.

### Finding Description
`depositETH` calls `_beforeDeposit`, which calls `_checkIfDepositAmountExceedesCurrentLimit`. For ETH, the check is:

```solidity
// LRTDepositPool.sol line 678-679
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));
}
```

`totalAssetDeposits` is computed by `getTotalAssetDeposits` → `getAssetDistributionData` → `getETHDistributionData`, where:

```solidity
// LRTDepositPool.sol line 480
ethLyingInDepositPool = address(this).balance;
```

The contract's raw ETH balance is included verbatim in the TVL calculation. The contract exposes an unrestricted `receive()`:

```solidity
// LRTDepositPool.sol line 58
receive() external payable { }
```

Any caller — including an attacker — can send ETH to `LRTDepositPool`. This ETH is immediately counted as `ethLyingInDepositPool` and flows into `getTotalAssetDeposits(ETH)`. If the resulting total exceeds `depositLimitByAsset(ETH)`, the check returns `true` and every call to `depositETH` reverts. The attacker's ETH cannot be swept out of the contract (no ETH sweep function exists in `LRTDepositPool`), so the inflated TVL persists until an admin raises the deposit limit.

Note the asymmetry: for LST assets the check is `totalAssetDeposits + amount > limit`, but for ETH it is `totalAssetDeposits > limit` — meaning even a 1-wei excess blocks deposits of any size.

### Impact Explanation
All ETH deposits via `depositETH` are blocked for every user until an admin governance action raises the deposit limit. Users cannot convert ETH to rsETH through the primary deposit path. This matches **Medium — Temporary freezing of funds**.

### Likelihood Explanation
The attack is cheap when the protocol TVL is near the deposit cap (a common operational state for risk-managed protocols). The attacker spends ETH that is locked in the protocol as TVL (not recoverable by the attacker, but also not easily removable by the protocol). The attacker can repeat the send after each admin limit increase to sustain the DOS. No special permissions are required — any externally-owned account can trigger it.

### Recommendation
- Restrict `receive()` to only accept ETH from known protocol addresses (NodeDelegator, RewardReceiver, LRTConverter, etc.), rejecting arbitrary senders.
- Alternatively, track a separate `depositedETH` accounting variable that is only incremented on legitimate deposit paths, and use that variable instead of `address(this).balance` in `getETHDistributionData`.
- Add an admin ETH sweep function to `LRTDepositPool` so that unsolicited ETH can be removed from the TVL calculation.

### Proof of Concept
1. Attacker reads `getTotalAssetDeposits(ETH_TOKEN)` → returns `X`.
2. Attacker reads `lrtConfig.depositLimitByAsset(ETH_TOKEN)` → returns `L`.
3. Attacker sends `L - X + 1 wei` to `LRTDepositPool` via a plain ETH transfer (hits `receive()`).
4. `address(LRTDepositPool).balance` increases by `L - X + 1`.
5. `getETHDistributionData().ethLyingInDepositPool` = old balance + `L - X + 1` > `L`.
6. Any user calling `depositETH(minRSETH, referralId)` now hits `_checkIfDepositAmountExceedesCurrentLimit` → returns `true` → reverts with `MaximumDepositLimitReached`.
7. ETH deposits are frozen until admin calls a setter to raise `depositLimitByAsset(ETH_TOKEN)`.

**Affected lines:** [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** contracts/LRTDepositPool.sol (L58-58)
```text
    receive() external payable { }
```

**File:** contracts/LRTDepositPool.sol (L480-480)
```text
        ethLyingInDepositPool = address(this).balance;
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
