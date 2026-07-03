Audit Report

## Title
Missing ETH Recovery Path Causes Temporary Freezing of Bridged Funds - (File: contracts/L1Vault.sol, contracts/L1VaultV2.sol)

## Summary
Both `L1Vault` and `L1VaultV2` accept ETH from the L2 bridge via `receive() external payable` but expose no direct ETH withdrawal or recovery function. The sole ETH exit path, `depositETHForL1VaultETH()`, unconditionally routes through `LRTDepositPool.depositETH()`, which reverts under several normal protocol conditions. When any of those conditions hold, bridged ETH accumulates in the vault with no alternative exit, causing temporary freezing of funds.

## Finding Description
`L1Vault` (L367–368) and `L1VaultV2` (L562–563) each declare:

```solidity
/// @dev Handles direct ETH transfers from the L2 bridge
receive() external payable { }
```

The only function that moves ETH out is `depositETHForL1VaultETH()` (L1Vault L150–161, L1VaultV2 L224–234):

```solidity
function depositETHForL1VaultETH() external payable nonReentrant onlyRole(MANAGER_ROLE) {
    uint256 balanceOfETH = address(this).balance;
    uint256 rsETHAmountToMint = lrtDepositPool.getRsETHAmountToMint(ETH_IDENTIFIER, balanceOfETH);
    if (rsETHAmountToMint == 0) { revert InvalidMinRSETHAmountExpected(); }
    lrtDepositPool.depositETH{ value: balanceOfETH }(rsETHAmountToMint, "");
    ...
}
```

`LRTDepositPool.depositETH()` (L76–93) carries the `whenNotPaused` modifier and delegates to `_beforeDeposit()` (L648–670), which reverts with `MaximumDepositLimitReached` when `totalAssetDeposits > lrtConfig.depositLimitByAsset(asset)` (L661–663, L676–682). It also reverts with `InvalidAmountToDeposit` when `depositAmount < minAmountToDeposit` (L657–658).

A `grep` across both vault files for `recoverETH`, `recoverTokens`, and `Recoverable` returns zero matches. `Recoverable.sol` (L64–73) exists in the codebase and provides an admin-gated `recoverETH()`, but neither vault inherits it.

Exploit path:
1. The L2 bridge sends ETH to `L1Vault` / `L1VaultV2` via `receive()`.
2. The LRT deposit pool's ETH deposit limit has been reached organically (no admin action required to reach this state).
3. The MANAGER calls `depositETHForL1VaultETH()` → `LRTDepositPool._beforeDeposit()` reverts with `MaximumDepositLimitReached`.
4. No other function in either vault can transfer ETH out.
5. All subsequently bridged ETH accumulates in the vault, frozen, until the admin raises the deposit limit.

## Impact Explanation
**Medium. Temporary freezing of funds.** ETH bridged from L2 is frozen inside `L1Vault` / `L1VaultV2` for as long as the deposit pool's limit remains at or below the current total deposits. The freeze is not permanent in the deposit-limit scenario (the admin can raise the cap), but the absence of any emergency recovery function means there is no protocol-level escape hatch independent of the deposit pool's state. Every ETH transfer from the L2 bridge during the blocked period adds to the frozen balance.

## Likelihood Explanation
No privileged attacker is required. The ETH deposit limit (`depositLimitByAsset`) is a finite protocol parameter that is reached through ordinary user deposits. Once reached, every subsequent L2→L1 bridge transfer of ETH lands in the vault with no exit. The L2 bridge is a production-facing component that operates continuously, making accumulation of frozen ETH a realistic and repeatable outcome.

## Recommendation
Inherit `Recoverable.sol` in both `L1Vault` and `L1VaultV2`, or add an explicit admin-gated recovery function:

```solidity
function recoverETH(address payable recipient, uint256 amount)
    external
    onlyRole(DEFAULT_ADMIN_ROLE)
{
    (bool ok,) = recipient.call{value: amount}("");
    require(ok, "ETH transfer failed");
}
```

This provides an independent exit path that does not depend on the deposit pool being operational, ensuring bridged ETH can always be recovered by the admin regardless of pool state.

## Proof of Concept
```solidity
// Foundry fork test outline
function test_ethFrozenWhenDepositLimitReached() public {
    // 1. Fork mainnet; obtain L1Vault and LRTDepositPool instances
    // 2. Prank the LRT admin to set ETH depositLimitByAsset to current totalAssetDeposits
    //    (simulating the limit being organically reached)
    // 3. Deal 10 ETH to the L2 bridge address; call L1Vault.receive() by sending ETH
    assertEq(address(l1Vault).balance, 10 ether);
    // 4. Prank MANAGER; call depositETHForL1VaultETH()
    vm.prank(manager);
    vm.expectRevert(ILRTDepositPool.MaximumDepositLimitReached.selector);
    l1Vault.depositETHForL1VaultETH();
    // 5. Confirm no other function can move the ETH out
    assertEq(address(l1Vault).balance, 10 ether); // still frozen
}
```