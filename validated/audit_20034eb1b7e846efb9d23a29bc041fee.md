### Title
`LRTOracle.updateRSETHPrice()` Automatic Pause Propagation Temporarily Freezes All L1 Deposits and Withdrawals - (File: contracts/LRTOracle.sol)

### Summary
`LRTOracle.updateRSETHPrice()` is a public, permissionless function. When the computed rsETH price drops beyond `pricePercentageLimit` relative to `highestRsethPrice`, it automatically pauses both `LRTDepositPool` and `LRTWithdrawalManager` without any admin action. This is a direct analog to the nested-RST issue: a child component (`LRTOracle`) independently transitions into a state that propagates a pause to the parent component (`LRTDepositPool`), blocking all user deposits and withdrawals until an admin manually unpauses.

### Finding Description
`LRTOracle._updateRsETHPrice()` contains the following automatic pause propagation logic:

```solidity
if (isPriceDecreaseOffLimit) {
    if (!lrtDepositPool.paused()) lrtDepositPool.pause();
    if (!withdrawalManager.paused()) withdrawalManager.pause();
    _pause();
    return;
}
``` [1](#0-0) 

This is invoked from `updateRSETHPrice()`, which is declared `public` with only a `whenNotPaused` guard on the oracle itself:

```solidity
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
``` [2](#0-1) 

`LRTDepositPool.depositETH()` and `depositAsset()` both carry `whenNotPaused`: [3](#0-2) 

Once `lrtDepositPool.pause()` is called from inside `_updateRsETHPrice()`, every subsequent call to `depositETH` or `depositAsset` reverts. The pause can only be lifted by an admin calling `unpause()`. [4](#0-3) 

The nested dependency chain is:
- **Child**: `LRTOracle` detects a price drop and autonomously calls `lrtDepositPool.pause()`.
- **Parent**: `LRTDepositPool` relies on not being paused to serve user deposits; it has no awareness of or control over the oracle's decision to pause it.

This mirrors the nested-RST pattern exactly: the child component (`LRTOracle`) independently enters a state (price-drop-triggered pause propagation) that silently blocks the parent component's (`LRTDepositPool`) core operation (issuance/deposit).

### Impact Explanation
Any user who calls `updateRSETHPrice()` when the rsETH price has dropped beyond `pricePercentageLimit` will trigger an automatic, protocol-wide pause of deposits and withdrawals. All L1 depositors are frozen until an admin manually unpauses. Additionally, `L1Vault.depositETHForL1VaultETH()` — which calls `lrtDepositPool.depositETH()` — also fails during this window, meaning ETH already bridged from L2 to L1 cannot be converted to rsETH and bridged back, leaving the L2 wrsETH partially unbacked. [5](#0-4) 

**Impact class**: Medium — Temporary freezing of funds.

### Likelihood Explanation
The trigger condition (rsETH price dropping beyond `pricePercentageLimit`) is realistic: EigenLayer slashing events, a supported LST depeg, or a sudden drop in underlying asset oracle prices can all cause the computed rsETH price to fall. Once conditions are met, any unprivileged user can call the public `updateRSETHPrice()` to lock the protocol. No admin collusion or key compromise is required.

### Recommendation
- Restrict `updateRSETHPrice()` to authorized callers (e.g., `MANAGER` or `OPERATOR` role), or add a keeper/bot whitelist, so that the automatic pause cannot be triggered by arbitrary users.
- Alternatively, separate the price-update logic from the pause-propagation logic: emit an event on threshold breach and let a separate, access-controlled function execute the pause, preventing a single public call from atomically freezing the protocol.

### Proof of Concept
1. A slashing event or LST depeg causes the on-chain TVL to drop, making `newRsETHPrice` fall more than `pricePercentageLimit` below `highestRsethPrice`.
2. Any unprivileged user calls `LRTOracle.updateRSETHPrice()`.
3. Inside `_updateRsETHPrice()`, `isPriceDecreaseOffLimit` evaluates to `true`.
4. The oracle calls `lrtDepositPool.pause()` and `withdrawalManager.pause()` autonomously.
5. All subsequent calls to `LRTDepositPool.depositETH()` and `depositAsset()` revert with `Pausable: paused`.
6. `L1Vault.depositETHForL1VaultETH()` also reverts, leaving bridged ETH stranded in the vault.
7. The freeze persists until an admin calls `lrtDepositPool.unpause()` — no user action can lift it. [6](#0-5) [7](#0-6)

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L270-282)
```text
        if (newRsETHPrice < highestRsethPrice) {
            uint256 diff = highestRsethPrice - newRsETHPrice;
            // normalizing to 1e18
            bool isPriceDecreaseOffLimit =
                pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);

            // if price decrease is off limit, pause the protocol (unless it's already paused)
            if (isPriceDecreaseOffLimit) {
                if (!lrtDepositPool.paused()) lrtDepositPool.pause();
                if (!withdrawalManager.paused()) withdrawalManager.pause();
                _pause();
                return;
            }
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

**File:** contracts/LRTDepositPool.sol (L348-356)
```text
    /// @dev Triggers stopped state. Contract must not be paused.
    function pause() external onlyRole(LRTConstants.PAUSER_ROLE) {
        _pause();
    }

    /// @dev Returns to normal state. Contract must be paused.
    function unpause() external onlyLRTAdmin {
        _unpause();
    }
```

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
