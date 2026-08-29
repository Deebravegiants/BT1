# [H] RedeemerWithFees::BASE_UNIT immutable variable and oracle changing leads to inconsistent state and causes RedeemerWithFees::dstableAmountToBaseValue returning wrong values

## Summary
Severity: High
Chain: Smart contract
Component: dTRINITY
Published: 2025-06-17
Source: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/108
Type: hats-finding

## Details
**Github username:** --
  **Twitter username:** --
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/tester)

  **Beneficiary:** 0x56A5E4beCc5148ef38F8aa75B500FF5e58eEd9D9
  **Submission hash (on-chain):** 0xd307afe585f3b98aeba592033e42e5077716a9c707ef8cff2355672545b90b4e
  **Severity:** high
  
  **Description:**
  **Description**\
RedeemerWithFees declares BASE_UNIT an immutable variable used to calculate the amount of dstable tokens needed to match a specific base value in dstableAmountToBaseValue function  
This immutable variable value is set in constructor with oracle parameter _oracle.BASE_CURRENCY_UNIT() result[1]:  
https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/blob/bef3b2af8c38552a9e697ff8eecfd9bdf3982834/contracts/dstable/RedeemerWithFees.sol#L85-L91  
```
    constructor(
        address _collateralVault,
        address _dstable,
@[1]>      IPriceOracleGetter _oracle,
        //...
@[2]>) OracleAware(_oracle, _oracle.BASE_CURRENCY_UNIT()) {
```
However as seen in [2] RedeemerWithFees inherits from OracleAware contract allowing to change its oracle  
https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/blob/bef3b2af8c38552a9e697ff8eecfd9bdf3982834/contracts/dstable/OracleAware.sol#L58-L65
```
    function setOracle(
        IPriceOracleGetter newOracle
    ) public onlyRole(DEFAULT_ADMIN_ROLE) {
        //...
@>      oracle = newOracle;
```
So if the new oracle set has oracle::BASE_CURRENCY_UNIT() != RedeemerWithFees::BASE_UNIT (this could be set using OracleAware::setBaseCurrencyUnit)  
https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/blob/bef3b2af8c38552a9e697ff8eecfd9bdf3982834/contracts/dstable/OracleAware.sol#L75
```
    function setBaseCurrencyUnit(
        uint256 _newBaseCurrencyUnit
    ) public onlyRole(DEFAULT_ADMIN_ROLE) {
        baseCurrencyUnit = _newBaseCurrencyUnit;
    }
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/108_
