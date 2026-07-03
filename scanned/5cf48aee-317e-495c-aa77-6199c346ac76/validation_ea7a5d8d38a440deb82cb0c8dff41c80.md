### Title
Unrestricted `sendFunds()` in `FeeReceiver` Permanently Locks Accidentally Sent ETH via Unrestricted `receive()` - (File: `contracts/FeeReceiver.sol`)

---

### Summary

`FeeReceiver.sol` has an unrestricted `receive()` function and a permissionless `sendFunds()` function that forwards the contract's entire ETH balance to the deposit pool. If ETH is accidentally sent to `FeeReceiver`, any unprivileged caller can invoke `sendFunds()` to permanently commit that ETH into the protocol TVL, with no recovery path available.

---

### Finding Description

`FeeReceiver` is designed to accumulate MEV and execution-layer rewards, then forward them to `LRTDepositPool` via `sendFunds()`. Three properties combine to create the vulnerability:

**1. `receive()` imposes no sender restriction:** [1](#0-0) 

Any address — including a user who accidentally sends ETH — can deposit ETH into the contract.

**2. `sendFunds()` has no access control:** [2](#0-1) 

The function is `external` with no role modifier. Any unprivileged caller can trigger it at any time.

**3. `sendFunds()` uses `address(this).balance` — the entire balance, not just legitimate reward ETH:** [3](#0-2) 

This means accidentally sent ETH is swept along with genuine MEV rewards.

**4. `FeeReceiver` has no recovery mechanism.** Unlike other contracts in the codebase that inherit `Recoverable` (which provides `recoverETH()` guarded by `DEFAULT_ADMIN_ROLE`), `FeeReceiver` has no such function: [4](#0-3) 

`FeeReceiver` does not inherit `Recoverable`, so once `sendFunds()` is called, the accidentally sent ETH is irretrievably added to the deposit pool TVL.

---

### Impact Explanation

**Impact: Medium — Permanent freezing of funds.**

Once an unprivileged caller invokes `sendFunds()`, the accidentally sent ETH is forwarded to `LRTDepositPool.receiveFromRewardReceiver()` and permanently absorbed into the protocol TVL. The original sender has no mechanism to recover their ETH. The ETH inflates the rsETH price slightly (benefiting all existing rsETH holders), but the sender suffers a total, irreversible loss of their accidentally sent funds.

---

### Likelihood Explanation

**Likelihood: Low.**

Accidental ETH sends to a specific contract address are uncommon but not unprecedented (e.g., wallet UI errors, copy-paste mistakes, contract interaction bugs). Once such an accident occurs, the window for exploitation is open indefinitely — any observer can call `sendFunds()` at any time to permanently commit the ETH. No special privileges or capital are required.

---

### Recommendation

1. **Restrict `sendFunds()` to an authorized role** (e.g., `LRTConstants.MANAGER`) so that only trusted operators can trigger the forwarding of the balance. This mirrors the pattern used in `FeeSplitter` in the referenced external report.

2. **Add a recovery function** (or inherit `Recoverable`) so that an admin can return accidentally sent ETH to its rightful owner before it is swept into the protocol.

```solidity
// Option 1: restrict sendFunds
function sendFunds() external onlyRole(LRTConstants.MANAGER) {
    uint256 balance = address(this).balance;
    ILRTDepositPool(depositPool).receiveFromRewardReceiver{ value: balance }();
    emit MevRewardsAddedToTVL(balance);
}

// Option 2: add ETH recovery
function recoverETH(address recipient, uint256 amount) external onlyRole(DEFAULT_ADMIN_ROLE) {
    (bool success,) = payable(recipient).call{ value: amount }("");
    require(success, "FeeReceiver: ETH transfer failed");
}
```

---

### Proof of Concept

1. Alice accidentally sends `1 ETH` directly to `FeeReceiver` (e.g., via a wallet UI error).
2. Bob, an unprivileged observer, notices the ETH balance of `FeeReceiver` has increased beyond expected MEV rewards.
3. Bob calls `FeeReceiver.sendFunds()` with no special role or capital.
4. `sendFunds()` reads `address(this).balance` — which includes Alice's `1 ETH` — and forwards the entire amount to `LRTDepositPool` via `receiveFromRewardReceiver`.
5. Alice's `1 ETH` is permanently absorbed into the protocol TVL. The rsETH price increases marginally. Alice has no recourse. [5](#0-4)

### Citations

**File:** contracts/FeeReceiver.sol (L49-57)
```text
    /// @dev fallback to receive funds
    receive() external payable { }

    /// @dev send all rewards to deposit pool
    function sendFunds() external {
        uint256 balance = address(this).balance;
        ILRTDepositPool(depositPool).receiveFromRewardReceiver{ value: balance }();

        emit MevRewardsAddedToTVL(balance);
```

**File:** contracts/utils/Recoverable.sol (L64-70)
```text
    function recoverETH(address recipient, uint256 amount) external onlyRole(DEFAULT_ADMIN_ROLE) {
        UtilLib.checkNonZeroAddress(recipient);
        if (amount == 0) revert ZeroAmount();
        if (address(this).balance < amount) revert InsufficientBalance();

        (bool success,) = payable(recipient).call{ value: amount }("");
        if (!success) revert TransferFailed();
```
