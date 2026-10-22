# [M] Loss of precision in the YieldVault causes DoS when depositing from the Vault

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-08-pooltogether-mitigation
Published: 2023-08-24
Source: https://github.com/code-423n4/2023-08-pooltogether-mitigation-findings/issues/79
Type: code-finding

## Details
# Lines of code

https://github.com/GenerationSoftware/pt-v5-vault/blob/main/src/Vault.sol#L1176-L1184


# Vulnerability details

# Title
Loss of precision in the YieldVault causes DoS when depositing from the Vault

## Original Issue
[M-22 - Loss of precision leads to undercollateralized](https://github.com/code-423n4/2023-07-pooltogether-findings/issues/143)

## Details
The original demonstrates how the Vault could fall into undercollateralization mode if the YieldVault rounds down the deposits causing a loss of precision.
- The problem was caused because the number of minted shares (_totalSupplyAmount) would be greater than the number of deposited assets in the YieldVault (_withdrawableAssets) because of the loss of precision when rounding down the amount of deposited assets in the YieldVault.

## Mitigation
The mitigation was to refactor the way the Vault determines if it's collateralized or not, as part of this change, the `_currentExchangeRate()` function was removed, and instead new logic was implemented to make that the shares are fully backed 1:1 to assets in the YieldVault.
Now, with the new logic, when depositing in the Vault, there is a check that validates if the deposited assets in the YieldVault were the exact amount of deposited assets.



### Conclusion of the Mitigation and Proof of Concept of the New Bug
The implemented mitigation prevents the Vault from falling into under-collateralization but now introduces a new bug where the deposits could fall into DoS because of the loss of precision in the YieldVault because most vaults will do rounds-down shares calculations.
For example: depositing `1000000000`, but it can only withdraw `999999999`.
- Using the above example with the new implementation:
  - 1. The vault will deposit into the YieldVault `1000000000`
  - 2. The YieldVault will cause the loss of precision, thus, the totalWithdrawableAssets in the YieldVault was increased by `999999999` instead of `1000000000`.
  - 3. The Vault will validate if the withdrawableAssetsAfter the deposit is greater than the previousWithdrawableAssets + the depositedAmount
  - 4. The check will fail because the withdrawableAssetsAfter is less than (previousWithdrawableAssets + the depositedAmount)
    - The reason is because **withdrawableAssetsAfter is actually (previousWithdrawableAssets + `999999999`)** (Because of the loss of precision)
    - **_expectedWithdrawableAssets == (previousWithdrawableAssets + `1000000000`)**

    - So **the check is actually comparing ==> (previousWithdrawableAssets + `999999999`) < (previousWithdrawableAssets + `1000000000`)**, thus, the tx will be reverted!

```solidity
function _deposit(
  address _caller,
  address _receiver,
  uint256 _assets
) internal onlyVaultCollateralized {
  // It is only possible to deposit when the vault is collateralized
  // Shares are backed 1:1 by assets
  if (_assets == 0) revert MintZeroShares();

  uint256 _vaultAssets = _asset.balanceOf(address(this));

  ...

  uint256 _withdrawableAssets = _totalAssets();

  _yieldVault.deposit(_assets, address(this));

  uint256 _expectedWithdrawableAssets = _withdrawableAssets + _assets;
  uint256 _withdrawableAssetsAfter = _totalAssets();

  if (_withdrawableAssetsAfter < _expectedWithdrawableAssets)
    revert YVWithdrawableAssetsLTExpected(_withdrawableAssetsAfter, _expectedWithdrawableAssets);

  _mint(_receiver, _assets);

  emit Deposit(_caller, _receiver, _assets, _assets);
}
```

### Coded PoC
- Add the below test to the [`Deposit.t.sol`](https://github.com/GenerationSoftware/pt-v5-vault/blob/main/test/unit/Vault/Deposit.t.sol) test file.
```solidity
function testLossPrecision() external {
  vm.startPrank(alice);
  
  //0.Constructing a yieldVault that is already profitable
  uint256 _amount = 333e18;
  underlyingAsset.mint(alice, _amount);
  underlyingAsset.approve(address(yieldVault), type(uint256).max);   
  yieldVault.deposit(_amount,alice);
  //profitable 0.1e18
  underlyingAsset.mint(address(yieldVault), 0.1e18);

  //1.alice deposit
  _amount = 100e18;
  underlyingAsset.mint(alice, _amount);
  underlyingAsset.approve(address(vault), type(uint256).max);
  vault.deposit(_amount, alice);
  return;
  }
```

- Run the PoC, the results will be similar to:
> forge test --match-test testLossPrecision
```
Running 1 test for test/unit/Vault/Deposit.t.sol:VaultDepositTest
[FAIL. Reason: YVWithdrawableAssetsLTExpected(99999999999999999999 [9.999e19], 100000000000000000000 [1e20])] testLossPrecision() (gas: 302275)
Test result: FAILED. 0 passed; 1 failed; 0 skipped; finished in 7.87ms
Ran 1 test suites: 0 tests passed, 1 failed, 0 skipped (1 total tests)

Failing tests:
Encountered 1 failing test in test/unit/Vault/Deposit.t.sol:VaultDepositTest
[FAIL. Reason: YVWithdrawableAssetsLTExpected(99999999999999999999 [9.999e19], 100000000000000000000 [1e20])] testLossPrecision() (gas: 302275)

Encountered a total of 1 failing tests, 0 tests succeeded
```

## Impact
Deposits will fall into DoS for `YieldVaults` that calculates shares rounding down when depositing (The exact same reason as the original issue)
- The cause of the new bug is the same reason as the original issue, but this time, **the consequence is a DoS on the Deposit functionality in the Vault** instead of causing the vault to fall into under-collateralization

## Recommended Mitigation Steps
- The recommendation to prevent the DoS would be to consider the loss of precision caused in the YieldVault when doing the deposit, and when calculating the `_expectedWithdrawableAssets`, instead of adding the exact amount of assets that were deposited in the YieldVault, compute the value after the loss of precision that will be caused in the YieldVault, in this way, if a loss of precision happens in the YieldVault, the `_expectedWithdrawableAssets` has already accounted for it, and the check will now compare the correct values.

```solidity
function _deposit(
  address _caller,
  address _receiver,
  uint256 _assets
) internal onlyVaultCollateralized {
  // It is only possible to deposit when the vault is collateralized
  // Shares are backed 1:1 by assets
  if (_assets == 0) revert MintZeroShares();

  uint256 _vaultAssets = _asset.balanceOf(address(this));

  ...

  uint256 _withdrawableAssets = _totalAssets();

  _yieldVault.deposit(_assets, address(this));

- uint256 _expectedWithdrawableAssets = _withdrawableAssets + _assets;

  //audit-info => Compute the value of assets with the loss of precision that happened in the YieldVault
+ uint256 amountWithLossOfPrecision = _assetsWithLossOfPrecission
+ uint256 _expectedWithdrawableAssets = _withdrawableAssets + amountWithLossOfPrecision;

  uint256 _withdrawableAssetsAfter = _totalAssets();

  if (_withdrawableAssetsAfter < _expectedWithdrawableAssets)
    revert YVWithdrawableAssetsLTExpected(_withdrawableAssetsAfter, _expectedWithdrawableAssets);

  _mint(_receiver, _assets);

  emit Deposit(_caller, _receiver, _assets, _assets);
}
```


## Assessed type

Context
