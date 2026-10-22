# [M] Large amounts of points can be minted multiple times

## Summary
Severity: Medium
Contest weight: 0.5966
Dataset id: 22433
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Large amounts of points can be minted virtually without any cost. The points are intended to be used to exchange something of value. A malicious user could abuse this to obtain a large number of points, which could obtain excessive value from the protocol and create unfairness among other protocol users.
When depositing stable collateral, the LPs only need to pay for the keeper fee. The keeper fee will be sent to the caller who executed the deposit order.
When withdrawing stable collateral, the LPs need to pay for the keeper fee and withdraw fee. However, there is an instance where one does not need to pay for the withdrawal fee. Per the condition at Line 120 below, if the totalSupply is zero, be applicable and remain at zero.
File: StableModule.sol
```solidity
function executeWithdraw(
    address _account,
    uint64 _executableAtTime,
    FlatcoinStructs.AnnouncedStableWithdraw calldata _announcedWithdraw
) external whenNotPaused onlyAuthorizedModule returns (uint256 _amountOut, uint256 _withdrawFee) {
    uint256 withdrawAmount = _announcedWithdraw.withdrawAmount;
..SNIP..
    _burn(_account, withdrawAmount);
..SNIP..
    // Check that there is no significant impact on stable token price.
    // This should never happen and means that too much value or not enough value was withdrawn.
    if (totalSupply() > 0) {
        if (
            stableCollateralPerShareAfter < stableCollateralPerShareBefore - 1e6 ||
            stableCollateralPerShareAfter > stableCollateralPerShareBefore + 1e6
        ) revert FlatcoinErrors.PriceImpactDuringWithdraw();

        _withdrawFee = (stableWithdrawFee * _amountOut) / 1e18;

        // additionalSkew = 0 because withdrawal was already processed above.
        vault.checkSkewMax({additionalSkew: 0});
    } else {
        // Need to check there are no longs open before allowing full system withdrawal.
        uint256 sizeOpenedTotal = vault.getVaultSummary().globalPositions.sizeOpenedTotal;

        if (sizeOpenedTotal != 0) revert FlatcoinErrors.MaxSkewReached(sizeOpenedTotal);
        if (stableCollateralPerShareAfter != 1e18) revert FlatcoinErrors.PriceImpactDuringFullWithdraw();
    }
```
When LPs deposit rETH and mint UNIT, the protocol will mint points to the depositor's account as per Line 84 below.
Assume that the vault has been newly deployed on-chain. Bob is the first LP to deposit rETH into the vault. Assume for a period of time (e.g., around 30 minutes), there are no other users depositing into the vault except for Bob.
Bob could perform the following actions to mint points for free:
• Bob announces a deposit order to deposit 100e18 rETH. Paid for the keeper fee. (Acting as a LP).
• Wait 10 seconds for the minExecutabilityAge to pass
• Bob executes the deposit order and mints 100e18 UNIT (Exchange rate 1:1). Protocol also mints 100e18 points to Bob's account. Bob gets back the keeper fee. (Acting as Keeper)
• Immediately after his executeDeposit TX, Bob inserts an "announce withdraw order" TX to withdraw all his 100e18 UNIT and pay for the keeper fee.
• Wait 10 seconds for the minExecutabilityAge to pass
• Bob executes the withdraw order and receives back his initial investment of 100e18 rETH. Since he is the only LP in the protocol, it is considered the got back his keeper fee. (Acting as Keeper)
Each attack requires 20 seconds (10 + 10) to be executed. Bob could rinse and repeat the attack until he was no longer the only LP in the system, where he had to pay for the withdraw fee, which might make this attack unprofitable.
If Bob is the only LP in the system for 30 minutes, he could gain 9000e18 points ((30 minutes / 20 seconds) * 100e18 ) for free as Bob could get back his keeper fee and does not incur any withdraw fee. The only thing that Bob needs to pay for is the gas fee, which is extremely cheap on L2 like Base.
File: StableModule.sol
```solidity
function executeDeposit(
    address _account,
    uint64 _executableAtTime,
    FlatcoinStructs.AnnouncedStableDeposit calldata _announcedDeposit
) external whenNotPaused onlyAuthorizedModule returns (uint256 _liquidityMinted) {
    uint256 depositAmount = _announcedDeposit.depositAmount;
..SNIP..
    _liquidityMinted = (depositAmount * (10 ** decimals())) / stableCollateralPerShare(maxAge);

..SNIP..
    _mint(_account, _liquidityMinted);

    vault.updateStableCollateralTotal(int256(depositAmount));
..SNIP..
    // Mint points
    IPointsModule pointsModule = IPointsModule(vault.moduleAddress(FlatcoinModuleKeys._POINTS_MODULE_KEY));
    pointsModule.mintDeposit(_account, _announcedDeposit.depositAmount);
```
Large amounts of points can be minted virtually without any cost. The points are intended to be used to exchange something of value. A malicious user could abuse this to obtain a large number of points, which could obtain excessive value from the protocol and create unfairness among other protocol users.

## Recommendation
One approach that could mitigate this risk is also to impose withdraw fee for the attack that was once not profitable due to the need to pay withdraw fee.
In addition, consider deducting the points once a position is closed or reduced in size so that no one can attempt to open and adjust/close a position repeatedly to obtain more points.
