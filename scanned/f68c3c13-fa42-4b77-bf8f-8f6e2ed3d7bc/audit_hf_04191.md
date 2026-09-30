# [M] `PrizeVault.maxDeposit`

## Summary
Severity: Medium
Contest weight: 0.5238
Dataset id: 20960
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Currently, `PrizeVault.maxDeposit()` calculates the maximum possible amount of deposit without taking into account produced fees. That means if there is already maxed deposited amount of asset that is calculated by the current implementation in `PrizeVault.maxDeposit()`, `yieldFeeRecipient` can’t withdraw shares with `PrizeVault.claimYieldFeeShares()` because in that case `_mint()` will revert because of overflow. A lot of low-price tokens can exceed the limit of `type(uint96).max` with ease. For example, to make a deposit with `maxDeposit()` value with LADYS token it’s needed only `$13568` (as of 08-03-2024).

If a user makes a maximum allowed deposit that is calculated by the current implementation of `PrizeVault.maxDeposit()`, `yieldFeeRecipient` can’t withdraw fees if they are available.

## Proof of Concept
Add this test to `PrizeVault.t.sol` and run with:
    
```bash
forge test --match-contract PrizeVaultTest --match-test testMaxDeposit_CalculatesWithoutTakingIntoAccountGeneratedFees
```

```solidity
function _deposit(address account, uint256 amount) private {
    underlyingAsset.mint(account, amount);
    vm.startPrank(account);
    underlyingAsset.approve(address(vault), amount);
    vault.deposit(amount, account);
    vm.stopPrank();
}

function testMaxDeposit_CalculatesWithoutTakingIntoAccountGeneratedFees() public {
    vault.setYieldFeePercentage(1e8); // 10%
    vault.setYieldFeeRecipient(bob);

    // alice make initial deposit
    _deposit(alice, 1e18);

    // mint yield to the vault and liquidate
    underlyingAsset.mint(address(vault), 1e18);
    vault.setLiquidationPair(address(this));
    uint256 maxLiquidation = vault.liquidatableBalanceOf(address(underlyingAsset));
    uint256 amountOut = maxLiquidation / 2;
    uint256 yieldFee = (1e18 - vault.yieldBuffer()) / (2 * 10); // 10% yield fee + 90% amountOut = 100%

    // bob transfers tokens out and increase fee
    vault.transferTokensOut(address(0), bob, address(underlyingAsset), amountOut);

    // alice make deposit with maximum available value for deposit
    uint256 maxDeposit = vault.maxDeposit(address(this));
    _deposit(alice, maxDeposit);

    // then bob want to withdraw earned fee but he can't do that
    vm.prank(bob);
    vm.expectRevert();
    vault.claimYieldFeeShares(yieldFee);
}
```

## Recommendation
Add function to withdraw fees in `asset` or change function `PrizeVault.maxDeposit()` to calculate max deposit with taking into account produced fees:
    
```diff
function maxDeposit(address) public view returns (uint256) {
    uint256 _totalSupply = totalSupply();
    uint256 totalDebt_ = _totalDebt(_totalSupply);
    if (totalAssets() < totalDebt_) return 0;

    // the vault will never mint more than 1 share per asset, so no need to convert supply limit to assets
    uint256 twabSupplyLimit_ = _twabSupplyLimit(_totalSupply);
    uint256 _maxDeposit;
    uint256 _latentBalance = _asset.balanceOf(address(this));
    uint256 _maxYieldVaultDeposit = yieldVault.maxDeposit(address(this));
    if (_latentBalance >= _maxYieldVaultDeposit) {
        return 0;
    } else {
        unchecked {
            _maxDeposit = _maxYieldVaultDeposit - _latentBalance;
        }
-           return twabSupplyLimit_ < _maxDeposit ? twabSupplyLimit_ : _maxDeposit;
+           return twabSupplyLimit_ < _maxDeposit ? twabSupplyLimit_ - yieldFeeBalance : _maxDeposit - yieldFeeBalance;
    }
}
```
