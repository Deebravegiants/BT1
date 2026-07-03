### Title
ETH Permanently Trapped in `L1Vault` and `L1VaultV2` With No Recovery Path - (File: contracts/L1Vault.sol, contracts/L1VaultV2.sol)

### Summary
`L1Vault` and `L1VaultV2` each declare a `receive()` function to accept ETH from the L2 bridge and from cross-chain fee refunds, but neither contract exposes any direct ETH withdrawal or recovery function. The sole path to move ETH out is `depositETHForL1VaultETH()`, which can revert under normal operational conditions, leaving ETH permanently locked with no alternative exit.

### Finding Description
Both `L1Vault` and `L1VaultV2` accept raw ETH via their `receive()` fallback:

`contracts/L1Vault.sol` line 368:
```solidity
/// @dev Handles direct ETH transfers from the L2 bridge
receive() external payable { }
```

`contracts/L1VaultV2.sol` line 563:
```solidity
/// @dev Handles direct ETH transfers from the L2 bridge
receive() external payable { }
```

The only function that can move ETH out of either contract is `depositETHForL1VaultETH()`:

```solidity
function depositETHForL1VaultETH() external payable nonReentrant onlyRole(MANAGER_ROLE) {
    uint256 balanceOfETH = address(this).balance;
    uint256 rsETHAmountToMint = lrtDepositPool.getRsETHAmountToMint(ETH_IDENTIFIER, balanceOfETH);
    if (rsETHAmountToMint == 0) {
        revert InvalidMinRSETHAmountExpected();
    }
    lrtDepositPool.depositETH{ value: balanceOfETH }(rsETHAmountToMint, "");
    ...
}
```

This function reverts in at least three realistic situations:
1. `rsETHAmountToMint == 0` — triggered when `balanceOfETH` is dust (very small amounts, e.g. from cross-chain fee refunds).
2. `LRTDepositPool` is paused — a routine security action that blocks `depositETH`.
3. The ETH deposit limit is reached — `_checkIfDepositAmountExceedesCurrentLimit` causes `depositETH` to revert with `MaximumDepositLimitReached`.

Neither `L1Vault` nor `L1VaultV2` inherits from `Recoverable` (which provides `recoverETH()`), and no other function exists to withdraw ETH to an arbitrary address. The contracts also do not implement any sweep or emergency-drain path for ETH.

In `L1VaultV2`, the CCIP bridging path (`bridgeRsETHToL2UsingCCIP`) sends native ETH to the CCIP router. Any ETH refunded by the router is returned to the contract (the contract is the `msg.sender` of `ccipSend`), adding another source of ETH accumulation with no exit.

### Impact Explanation
ETH received by `L1Vault` / `L1VaultV2` — whether from the L2 bridge, from cross-chain fee refunds, or from accidental direct sends — becomes permanently frozen whenever `depositETHForL1VaultETH()` is unavailable (pool paused, deposit limit reached) or reverts on dust amounts. There is no alternative function to recover or redirect the ETH. This constitutes a **permanent freezing of funds** (Critical) in the dust/refund case, or at minimum a **temporary freezing of funds** (Medium) while the pool is paused or at its limit.

### Likelihood Explanation
Medium. The L2 bridge regularly sends ETH to `L1Vault`. The LRT deposit pool is routinely paused for upgrades and security incidents. Deposit limits are a normal operational constraint. Cross-chain fee refunds (LayerZero, CCIP) are a documented and expected source of ETH. Any of these conditions, individually, is sufficient to strand ETH in the contract.

### Recommendation
Add an ETH recovery function to both `L1Vault` and `L1VaultV2`, restricted to the admin or timelock role, analogous to the existing `Recoverable.recoverETH()` pattern already present in the codebase:

```solidity
function recoverETH(address recipient, uint256 amount) external onlyRole(TIMELOCK_ROLE) {
    (bool success,) = payable(recipient).call{ value: amount }("");
    require(success, "ETH transfer failed");
    emit ETHRecovered(recipient, amount);
}
```

Alternatively, have both contracts inherit from `contracts/utils/Recoverable.sol`.

### Proof of Concept

1. The L2 bridge sends 1 ETH to `L1Vault` via `receive()`.
2. The LRT deposit pool is paused (routine security action).
3. The manager calls `depositETHForL1VaultETH()` — it calls `lrtDepositPool.depositETH()`, which reverts because the pool is paused (`whenNotPaused` modifier).
4. No other function in `L1Vault` can move the ETH out.
5. ETH is frozen until the pool is unpaused **and** `depositETHForL1VaultETH()` succeeds — but if the deposit limit is also reached at that point, the ETH remains permanently stuck.

For the dust case: if 1 wei of ETH arrives as a CCIP refund, `getRsETHAmountToMint(ETH_IDENTIFIER, 1)` returns 0, causing `depositETHForL1VaultETH()` to revert with `InvalidMinRSETHAmountExpected`, permanently trapping the dust with no recovery path. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/L1Vault.sol (L150-161)
```text
    function depositETHForL1VaultETH() external payable nonReentrant onlyRole(MANAGER_ROLE) {
        uint256 balanceOfETH = address(this).balance;
        uint256 rsETHAmountToMint = lrtDepositPool.getRsETHAmountToMint(ETH_IDENTIFIER, balanceOfETH);

        if (rsETHAmountToMint == 0) {
            revert InvalidMinRSETHAmountExpected();
        }

        lrtDepositPool.depositETH{ value: balanceOfETH }(rsETHAmountToMint, "");

        emit ETHDepositForL1Vault(balanceOfETH, rsETHAmountToMint);
    }
```

**File:** contracts/L1Vault.sol (L367-368)
```text
    /// @dev Handles direct ETH transfers from the L2 bridge
    receive() external payable { }
```

**File:** contracts/L1VaultV2.sol (L224-235)
```text
    function depositETHForL1VaultETH() external payable nonReentrant onlyRole(MANAGER_ROLE) {
        uint256 balanceOfETH = address(this).balance;
        uint256 rsETHAmountToMint = lrtDepositPool.getRsETHAmountToMint(ETH_IDENTIFIER, balanceOfETH);

        if (rsETHAmountToMint == 0) {
            revert InvalidMinRSETHAmountExpected();
        }

        lrtDepositPool.depositETH{ value: balanceOfETH }(rsETHAmountToMint, "");

        emit ETHDepositForL1Vault(balanceOfETH, rsETHAmountToMint);
    }
```

**File:** contracts/L1VaultV2.sol (L562-563)
```text
    /// @dev Handles direct ETH transfers from the L2 bridge
    receive() external payable { }
```

**File:** contracts/utils/Recoverable.sol (L64-73)
```text
    function recoverETH(address recipient, uint256 amount) external onlyRole(DEFAULT_ADMIN_ROLE) {
        UtilLib.checkNonZeroAddress(recipient);
        if (amount == 0) revert ZeroAmount();
        if (address(this).balance < amount) revert InsufficientBalance();

        (bool success,) = payable(recipient).call{ value: amount }("");
        if (!success) revert TransferFailed();

        emit ETHRecovered(recipient, amount);
    }
```
