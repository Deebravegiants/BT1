Audit Report

## Title
ETH Deposit DoS via Unsolicited `receive()` Balance Inflation in `_checkIfDepositAmountExceedesCurrentLimit` - (File: contracts/LRTDepositPool.sol)

## Summary
`getETHDistributionData()` computes total protocol ETH using raw `address(this).balance`, `nodeDelegatorQueue[i].balance`, and `lrtUnstakingVault.balance`. All three contracts expose an unrestricted `receive()` function, allowing any attacker to inflate these balances. Once the inflated sum exceeds `depositLimitByAsset(ETH)`, every call to `depositETH` reverts with `MaximumDepositLimitReached`, temporarily freezing ETH deposits for all users until an admin raises the limit.

## Finding Description
`getETHDistributionData()` reads raw native-ETH balances across three contracts:

```solidity
ethLyingInDepositPool = address(this).balance;          // LRTDepositPool.sol:480
ethLyingInNDCs += nodeDelegatorQueue[i].balance;        // LRTDepositPool.sol:485
ethLyingInUnstakingVault = lrtUnstakingVault.balance;   // LRTDepositPool.sol:496
```

These values feed into `getTotalAssetDeposits(ETH)` via `getAssetDistributionData`, which is consumed by `_checkIfDepositAmountExceedesCurrentLimit`:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));  // no `+ amount`
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

For ETH, `msg.value` is already reflected in `address(this).balance` at call time, so the check is a plain `>` with no separate addition. This is correct for legitimate deposits, but it means any ETH arriving via the open `receive()` function also inflates `totalAssetDeposits` without going through the deposit gate.

All three balance sources accept arbitrary ETH from any sender:
- `LRTDepositPool`: `receive() external payable { }` (line 58) — no access control, no accounting
- `LRTUnstakingVault`: `receive() external payable { emit EthReceived(...); }` (line 81-83)
- `NodeDelegator`: `receive() external payable { emit ETHReceived(...); }` (line 81-83)

An attacker sends `L - D + 1` wei to any of these addresses (where `D = getTotalAssetDeposits(ETH)` and `L = depositLimitByAsset(ETH)`). `getETHDistributionData()` now returns an inflated sum exceeding `L`. Every subsequent call to `depositETH` hits `_beforeDeposit` → `_checkIfDepositAmountExceedesCurrentLimit` → returns `true` → `revert MaximumDepositLimitReached()`. The attacker's ETH is not lost; it remains in the protocol, so the attack can be repeated at negligible marginal cost each time an admin raises the limit.

## Impact Explanation
**Medium — Temporary freezing of funds.** All ETH deposits via `depositETH` are blocked. Users cannot mint rsETH with ETH. The freeze persists until an admin raises `depositLimitByAsset(ETH)`. Because the attacker's ETH remains in the protocol, the admin must account for the inflated balance when resetting the limit, or the DoS can be re-triggered immediately.

## Likelihood Explanation
**Medium.** The attack requires no special role or permission — only the ability to send ETH to a public `receive()` function. The cost is the gap between the current `getTotalAssetDeposits(ETH)` and the configured limit. Protocols routinely operate near their deposit caps during high-demand periods, making the gap small. The attacker's ETH is not destroyed, enabling indefinite repetition at low marginal cost.

## Recommendation
Replace raw `address.balance` reads in `getETHDistributionData()` with an internal accounting variable (e.g., `ethDeposited`) that is incremented only through controlled entry points (`depositETH`, `receiveFromNodeDelegator`, `receiveFromRewardReceiver`, `receiveFromLRTConverter`). Unsolicited ETH arriving via the bare `receive()` function should either be rejected (revert) or tracked in a separate variable excluded from the deposit-limit calculation. This ensures `totalAssetDeposits` cannot be manipulated by external actors sending ETH directly.

## Proof of Concept
1. Read `D = lrtDepositPool.getTotalAssetDeposits(ETH_TOKEN)` and `L = lrtConfig.depositLimitByAsset(ETH_TOKEN)`.
2. Attacker executes `(bool ok,) = address(lrtDepositPool).call{value: L - D + 1}("");` (or sends to any NDC or `lrtUnstakingVault`).
3. `getETHDistributionData()` now returns `ethLyingInDepositPool` inflated by `L - D + 1`.
4. `getTotalAssetDeposits(ETH)` = `L + 1`.
5. `_checkIfDepositAmountExceedesCurrentLimit(ETH, any)` returns `true` (`L + 1 > L`).
6. Any user calling `depositETH(...)` reverts with `MaximumDepositLimitReached`.
7. ETH deposits are frozen for all users until admin raises the limit.

**Foundry test sketch:**
```solidity
function testBalanceInflationDoS() public {
    uint256 limit = lrtConfig.depositLimitByAsset(ETH_TOKEN);
    uint256 current = lrtDepositPool.getTotalAssetDeposits(ETH_TOKEN);
    uint256 gap = limit - current + 1;

    vm.deal(attacker, gap);
    vm.prank(attacker);
    (bool ok,) = address(lrtDepositPool).call{value: gap}("");
    assertTrue(ok);

    vm.deal(user, 1 ether);
    vm.prank(user);
    vm.expectRevert(ILRTDepositPool.MaximumDepositLimitReached.selector);
    lrtDepositPool.depositETH{value: 1 ether}(0, "");
}
```