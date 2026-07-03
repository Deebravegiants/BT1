### Title
ETH Deposit DoS via Raw `address.balance` Inflation in `getTotalAssetDeposits` - (File: contracts/LRTDepositPool.sol)

---

### Summary
`LRTDepositPool.getETHDistributionData()` computes total protocol ETH using raw `address(this).balance`, `nodeDelegatorQueue[i].balance`, and `lrtUnstakingVault.balance`. Because all three contracts expose an open `receive()` function, any attacker can forcibly inflate these balances. Once the inflated sum exceeds the configured deposit limit, every call to `depositETH` reverts with `MaximumDepositLimitReached`, freezing ETH deposits for all users.

---

### Finding Description

`getETHDistributionData()` reads raw native-ETH balances to account for ETH held across the protocol: [1](#0-0) 

```solidity
ethLyingInDepositPool = address(this).balance;
...
ethLyingInNDCs += nodeDelegatorQueue[i].balance;
...
ethLyingInUnstakingVault = lrtUnstakingVault.balance;
```

This feeds directly into `getTotalAssetDeposits(ETH)`, which is consumed by `_checkIfDepositAmountExceedesCurrentLimit`: [2](#0-1) 

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));
}
```

Note the asymmetry: for ERC-20 assets the incoming `amount` is added before comparing (`totalAssetDeposits + amount > limit`), but for ETH the incoming `msg.value` is already reflected in `address(this).balance` at call time, so the check is a plain `>` with no separate addition. This means that if `totalAssetDeposits` already exceeds the limit before any new deposit arrives, **every** subsequent `depositETH` call reverts.

All three balance sources accept arbitrary ETH:

- `LRTDepositPool`: [3](#0-2) 
- `LRTUnstakingVault`: [4](#0-3) 
- `NodeDelegator`: [5](#0-4) 

An attacker sends enough ETH to any one of these addresses to push `totalAssetDeposits` past `depositLimitByAsset(ETH)`. From that point on, `_beforeDeposit` reverts for every caller: [6](#0-5) 

```solidity
if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
    revert MaximumDepositLimitReached();
}
```

The attacker's ETH is not lost — it sits in the protocol — but the deposit gate is permanently tripped until an admin raises the limit. The attack cost equals the gap between the current total and the configured limit, which can be small when the protocol is near capacity.

---

### Impact Explanation

**Temporary freezing of funds (Medium).** All ETH deposits via `depositETH` are blocked. Users cannot mint rsETH with ETH. The freeze persists until an admin raises `depositLimitByAsset(ETH)`. Because the attacker's ETH remains in the protocol, the admin must also account for the inflated balance when resetting the limit, or the DoS can be re-triggered immediately at negligible marginal cost.

---

### Likelihood Explanation

**Medium.** The attack requires no special role or permission — only the ability to send ETH to a public `receive()` function. The cost is the difference between the current `getTotalAssetDeposits(ETH)` and the configured limit. Protocols routinely operate near their deposit caps (especially during high-demand periods), making the gap small and the attack cheap. The attacker loses the ETH sent but can grief the protocol indefinitely by repeating the attack each time the admin raises the limit.

---

### Recommendation

Replace raw `address.balance` reads with an internal accounting variable that is incremented only through controlled entry points (e.g., `receiveFromNodeDelegator`, `receiveFromRewardReceiver`). Unsolicited ETH arriving via `receive()` should either be rejected or tracked separately and excluded from the deposit-limit calculation. This mirrors the `create_idempotent` fix in the original report: use a state variable that cannot be manipulated by external actors rather than an observable that anyone can inflate.

---

### Proof of Concept

1. Observe current `getTotalAssetDeposits(ETH)` = `D` and `depositLimitByAsset(ETH)` = `L` where `D < L`.
2. Attacker calls `address(lrtDepositPool).call{value: L - D + 1}("")` (or sends to any NDC / unstaking vault).
3. `getETHDistributionData()` now returns `ethLyingInDepositPool` inflated by `L - D + 1`.
4. `getTotalAssetDeposits(ETH)` = `L + 1 > L`.
5. Any user calling `depositETH(...)` hits `_checkIfDepositAmountExceedesCurrentLimit` → returns `true` → `revert MaximumDepositLimitReached()`.
6. ETH deposits are frozen for all users until admin intervention.

### Citations

**File:** contracts/LRTDepositPool.sol (L58-58)
```text
    receive() external payable { }
```

**File:** contracts/LRTDepositPool.sol (L480-496)
```text
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
```

**File:** contracts/LRTDepositPool.sol (L661-663)
```text
        if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
            revert MaximumDepositLimitReached();
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

**File:** contracts/LRTUnstakingVault.sol (L81-83)
```text
    receive() external payable {
        emit EthReceived(msg.sender, msg.value);
    }
```

**File:** contracts/NodeDelegator.sol (L81-83)
```text
    receive() external payable {
        emit ETHReceived(msg.sender, msg.value);
    }
```
