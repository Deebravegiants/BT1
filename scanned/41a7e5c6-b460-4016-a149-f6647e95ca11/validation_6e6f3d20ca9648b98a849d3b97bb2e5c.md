### Title
L1Vault and L1VaultV2 Lock ETH With No Recovery Path When Deposit Pool Is Unavailable - (File: contracts/L1Vault.sol, contracts/L1VaultV2.sol)

### Summary
`L1Vault` and `L1VaultV2` each expose a `receive() external payable` function that is explicitly designed to accept ETH from the L2 bridge. However, neither contract contains any direct ETH withdrawal or recovery function. The sole mechanism to move ETH out of these contracts — `depositETHForL1VaultETH()` — routes funds into `LRTDepositPool.depositETH()`, which can revert under normal protocol conditions (deposit limit reached, pool paused, oracle returning zero). When that path is blocked, ETH sent from the L2 bridge is permanently trapped with no alternative exit.

### Finding Description
Both `L1Vault` and `L1VaultV2` declare:

```solidity
/// @dev Handles direct ETH transfers from the L2 bridge
receive() external payable { }
``` [1](#0-0) [2](#0-1) 

The only function that can move this ETH out is `depositETHForL1VaultETH()`:

```solidity
function depositETHForL1VaultETH() external payable nonReentrant onlyRole(MANAGER_ROLE) {
    uint256 balanceOfETH = address(this).balance;
    uint256 rsETHAmountToMint = lrtDepositPool.getRsETHAmountToMint(ETH_IDENTIFIER, balanceOfETH);
    if (rsETHAmountToMint == 0) {
        revert InvalidMinRSETHAmountExpected();
    }
    lrtDepositPool.depositETH{ value: balanceOfETH }(rsETHAmountToMint, "");
``` [3](#0-2) 

This function will revert if:
- `rsETHAmountToMint == 0` (oracle price anomaly)
- `LRTDepositPool.depositETH` reverts because the pool is paused (`whenNotPaused`)
- The ETH deposit limit is reached (`MaximumDepositLimitReached`)
- `depositAmount < minAmountToDeposit` [4](#0-3) 

There is no `recoverETH`, `withdrawETH`, or any other function that transfers ETH to an arbitrary recipient. A search across both files confirms zero such functions exist. [5](#0-4) 

### Impact Explanation
ETH bridged from L2 to `L1Vault` / `L1VaultV2` via the `receive()` path becomes permanently inaccessible whenever `depositETHForL1VaultETH()` cannot execute. Because there is no alternative ETH exit path, the funds are frozen inside the contract. The deposit limit being reached is a routine protocol state (not an admin attack), making this a realistic trigger. Impact: **temporary-to-permanent freezing of bridged ETH funds**.

### Likelihood Explanation
The L2 bridge is an active, production-facing component. ETH is expected to arrive at `L1Vault` / `L1VaultV2` regularly. The LRT deposit pool enforces a per-asset deposit limit (`depositLimitByAsset`) that can be reached organically. Once reached, every subsequent ETH transfer from the L2 bridge accumulates in the vault with no exit. No privileged attacker is required; the condition arises from normal protocol usage. [6](#0-5) 

### Recommendation
Add a direct ETH recovery function to both `L1Vault` and `L1VaultV2`, restricted to an appropriate privileged role (e.g., `DEFAULT_ADMIN_ROLE` or `TIMELOCK_ROLE`):

```solidity
function recoverETH(address payable recipient, uint256 amount)
    external
    onlyRole(DEFAULT_ADMIN_ROLE)
{
    (bool ok,) = recipient.call{value: amount}("");
    require(ok, "ETH transfer failed");
}
```

Alternatively, inherit from `Recoverable.sol`, which already provides `recoverETH()` and `recoverTokens()` with admin-gated access. [7](#0-6) 

### Proof of Concept
1. The L2 bridge sends 10 ETH to `L1Vault` via `receive()`.
2. The LRT deposit pool has reached its ETH deposit limit.
3. The MANAGER calls `depositETHForL1VaultETH()` → `LRTDepositPool.depositETH()` reverts with `MaximumDepositLimitReached`.
4. No other function in `L1Vault` can transfer ETH out.
5. The 10 ETH is permanently locked in `L1Vault` until the admin raises the deposit limit — but even then, the only exit is through the deposit pool, not a direct recovery. If the pool is permanently shut down, the ETH is irrecoverable. [8](#0-7) [9](#0-8)

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

**File:** contracts/L1VaultV2.sol (L224-234)
```text
    function depositETHForL1VaultETH() external payable nonReentrant onlyRole(MANAGER_ROLE) {
        uint256 balanceOfETH = address(this).balance;
        uint256 rsETHAmountToMint = lrtDepositPool.getRsETHAmountToMint(ETH_IDENTIFIER, balanceOfETH);

        if (rsETHAmountToMint == 0) {
            revert InvalidMinRSETHAmountExpected();
        }

        lrtDepositPool.depositETH{ value: balanceOfETH }(rsETHAmountToMint, "");

        emit ETHDepositForL1Vault(balanceOfETH, rsETHAmountToMint);
```

**File:** contracts/L1VaultV2.sol (L562-563)
```text
    /// @dev Handles direct ETH transfers from the L2 bridge
    receive() external payable { }
```

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

**File:** contracts/LRTDepositPool.sol (L657-664)
```text
        if (depositAmount == 0 || depositAmount < minAmountToDeposit) {
            revert InvalidAmountToDeposit();
        }

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
