### Title
Dust ETH Sent Directly to `LRTDepositPool` Inflates `totalAssetDeposits`, Blocking All ETH Deposits - (File: contracts/LRTDepositPool.sol)

---

### Summary

`LRTDepositPool.getETHDistributionData()` uses the raw `address(this).balance` to measure ETH held in the pool. Because the contract has an open `receive()` fallback, any unprivileged actor can send a tiny amount of ETH directly to the contract, inflating the reported `totalAssetDeposits` for ETH above the configured deposit limit and causing every subsequent `depositETH` call to revert with `MaximumDepositLimitReached`.

---

### Finding Description

`getETHDistributionData` reports the deposit-pool's ETH share as the raw contract balance: [1](#0-0) 

```solidity
ethLyingInDepositPool = address(this).balance;
```

This value feeds directly into `getTotalAssetDeposits`, which is then consumed by the deposit-limit guard: [2](#0-1) 

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));
    }
    ...
}
```

Two properties make this exploitable:

1. **Open receive fallback** — anyone can push ETH into the contract at any time: [3](#0-2) 

2. **ETH check omits the incoming deposit amount** — unlike the LST branch (`totalAssetDeposits + amount > limit`), the ETH branch only tests the *current* balance against the limit. A single wei of dust sent directly is enough to tip the balance over the limit when the protocol is near capacity.

The guard is invoked on every `depositETH` call: [4](#0-3) 

```solidity
if (depositAmount == 0 || depositAmount < minAmountToDeposit) {
    revert InvalidAmountToDeposit();
}
if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
    revert MaximumDepositLimitReached();
}
```

---

### Impact Explanation

All ETH deposits via `depositETH` are blocked until an operator manually moves ETH out of the deposit pool to a NodeDelegator (reducing `address(this).balance`) or raises the deposit limit. This constitutes a **temporary freezing of user funds** — users cannot deposit ETH and receive rsETH for an indefinite period controlled by the attacker's ability to re-send dust after each operator remediation.

**Impact: Medium — Temporary freezing of funds.**

---

### Likelihood Explanation

The `receive()` fallback is unconditionally open. The attack is cheapest (1 wei) when the protocol is operating near its deposit cap, which is a normal steady-state condition. No special permissions, front-running, or external protocol compromise is required. Any externally reachable account can execute this.

**Likelihood: Medium** — requires the protocol to be near its ETH deposit limit, which is a routine operational state.

---

### Recommendation

Replace the raw `address(this).balance` accounting with an internal tracked variable (e.g., `ethReceivedFromDepositors`) that is incremented only through the controlled deposit path and decremented when ETH is transferred out to NodeDelegators. Alternatively, mirror the LST branch and add the incoming `depositAmount` to `totalAssetDeposits` before comparing against the limit, so that unsolicited ETH does not count toward the cap.

---

### Proof of Concept

1. Protocol ETH deposit limit is set to `1_000 ether`; current `totalAssetDeposits` for ETH is `999.9999 ether`.
2. Attacker calls `(bool ok,) = address(lrtDepositPool).call{value: 1}("")` — costs 1 wei.
3. `address(lrtDepositPool).balance` increases by 1 wei.
4. `getETHDistributionData()` now returns `ethLyingInDepositPool = 999.9999 ether + 1 wei`.
5. `getTotalAssetDeposits(ETH_TOKEN)` exceeds `1_000 ether`.
6. `_checkIfDepositAmountExceedesCurrentLimit` returns `true`.
7. Every call to `depositETH(...)` reverts with `MaximumDepositLimitReached`.
8. Attacker repeats step 2 after each operator remediation to sustain the DoS.

### Citations

**File:** contracts/LRTDepositPool.sol (L58-58)
```text
    receive() external payable { }
```

**File:** contracts/LRTDepositPool.sol (L480-480)
```text
        ethLyingInDepositPool = address(this).balance;
```

**File:** contracts/LRTDepositPool.sol (L657-663)
```text
        if (depositAmount == 0 || depositAmount < minAmountToDeposit) {
            revert InvalidAmountToDeposit();
        }

        if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
            revert MaximumDepositLimitReached();
        }
```

**File:** contracts/LRTDepositPool.sol (L676-681)
```text
    function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
        uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
        if (asset == LRTConstants.ETH_TOKEN) {
            return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));
        }
        return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
```
