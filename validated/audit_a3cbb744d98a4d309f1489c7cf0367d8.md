### Title
Unguarded `receiveFromNodeDelegator()` Allows Any EOA to Inflate ETH Balance and Permanently Trigger Deposit Limit DoS — (File: contracts/LRTDepositPool.sol)

---

### Summary

`receiveFromNodeDelegator()` carries no caller restriction. Any EOA can call it with arbitrary `msg.value`, inflating `address(this).balance`. Because `getETHDistributionData()` feeds `address(this).balance` directly into `getTotalAssetDeposits(ETH_TOKEN)`, and because `_checkIfDepositAmountExceedesCurrentLimit` for ETH uses a strict-greater-than check against the deposit limit **without adding the incoming amount** (unlike the ERC20 branch), an attacker can push the running total above the configured cap and permanently block `depositETH()` until an admin manually raises the limit.

---

### Finding Description

**Entry point — no access control:**

```solidity
// LRTDepositPool.sol line 67
function receiveFromNodeDelegator() external payable { }
```

Any EOA may call this with any `msg.value`. The ETH lands in `address(this).balance`. [1](#0-0) 

**ETH accounting uses raw contract balance:**

```solidity
// LRTDepositPool.sol line 480
ethLyingInDepositPool = address(this).balance;
```

Every wei sent by the attacker is immediately reflected in `getTotalAssetDeposits(ETH_TOKEN)`. [2](#0-1) 

**Asymmetric limit check for ETH — does not add `amount`:**

```solidity
// LRTDepositPool.sol lines 678-679
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));
}
```

For ERC20 assets the check is `totalAssetDeposits + amount > limit`. For ETH it is only `totalAssetDeposits > limit`. Once the attacker's donation pushes the total past the cap, **every subsequent call to `depositETH()` reverts** with `MaximumDepositLimitReached`, regardless of the user's deposit size. [3](#0-2) 

**`depositETH()` gate:**

```solidity
// LRTDepositPool.sol lines 661-663
if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
    revert MaximumDepositLimitReached();
}
``` [4](#0-3) 

**Note on `receive()`:** The bare `receive() external payable {}` at line 58 provides the same inflation path, so the root cause is the combination of untracked ETH inflows and the raw-balance accounting — not solely `receiveFromNodeDelegator()`. However, `receiveFromNodeDelegator()` is the named, semantically-intended path for this question and is equally exploitable. [5](#0-4) 

---

### Impact Explanation

Once `getTotalAssetDeposits(ETH_TOKEN) > depositLimitByAsset[ETH_TOKEN]`, `depositETH()` is permanently gated until an admin calls `updateAssetDepositLimit`. The attacker's ETH is not recoverable by the attacker (it becomes protocol backing), but the cost to execute the attack is only `(depositLimit − currentTotal) + 1 wei`. At near-capacity state this is trivially cheap. New depositors are locked out for an indefinite period — **Medium: Temporary freezing of funds** (DoS on new ETH deposits).

---

### Likelihood Explanation

- No privileged role required; any EOA suffices.
- Cost scales with remaining headroom under the deposit limit; near-capacity it approaches 1 wei.
- The attacker forfeits the ETH but gains no rsETH, making it a pure griefing vector.
- The state persists until admin intervention, which may take hours to days.

---

### Recommendation

1. **Add caller restriction to `receiveFromNodeDelegator()`** — only registered NodeDelegator contracts (i.e., `isNodeDelegator[msg.sender] == 1`) should be able to call it.
2. **Track ETH deposits separately from raw balance** — maintain an internal accounting variable incremented only on legitimate `depositETH()` calls, and use that variable (not `address(this).balance`) in `getETHDistributionData()` for the deposit-limit check.
3. **Align the ETH limit check with the ERC20 check** — add `amount` to `totalAssetDeposits` before comparing against the limit, so a single large deposit that would breach the cap is rejected rather than all future deposits being blocked.

---

### Proof of Concept

```solidity
// Assume depositLimitByAsset[ETH_TOKEN] = 100 ether
// Assume getTotalAssetDeposits(ETH_TOKEN) = 99.9 ether (near cap)

// Step 1: attacker sends 0.1 ether + 1 wei via receiveFromNodeDelegator
ILRTDepositPool(pool).receiveFromNodeDelegator{value: 0.1 ether + 1}();

// Step 2: getTotalAssetDeposits(ETH_TOKEN) is now 100 ether + 1 wei
// _checkIfDepositAmountExceedesCurrentLimit returns true for ANY amount

// Step 3: any user attempting depositETH reverts
pool.depositETH{value: 1 ether}(0, ""); // reverts: MaximumDepositLimitReached

// State persists until admin raises the limit via updateAssetDepositLimit
```

The "block timestamp boundary" and `withdrawalDelayBlocks` framing in the question are not relevant to this exploit path — the DoS is purely balance-accounting-based and requires no timing manipulation.

### Citations

**File:** contracts/LRTDepositPool.sol (L58-58)
```text
    receive() external payable { }
```

**File:** contracts/LRTDepositPool.sol (L66-67)
```text
    /// @dev receive from NodeDelegator
    function receiveFromNodeDelegator() external payable { }
```

**File:** contracts/LRTDepositPool.sol (L480-480)
```text
        ethLyingInDepositPool = address(this).balance;
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
