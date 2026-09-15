# [H] The withdraw amount from EulerStragety.sol is not accurate, the passed in _amount is not the same as the amount of token withdraw and transferred to core contract

## Summary
Severity: High
Reporter: ctf_sec
Source: https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/EulerStrategy.sol#L77
Type: audit-issue

## Details
# The withdraw amount from EulerStragety.sol is not accurate, the passed in _amount is not the same as the amount of token withdraw and transferred to core contract

## Summary

The withdraw amount from EulerStragety.sol is not accurate in the function

```solidity
function _withdraw(uint256 _amount) internal override
```

the passed in _amount is not the same as the amount of token withdraw and transferred to core contract.

## Vulnerability Detail

in the function _withdraw in EulerStragety.sol, the function try to withdraw the amount of token 
and transfer the withdraw amount to the Core contract.

https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/EulerStrategy.sol#L77

```solidity
  function _withdraw(uint256 _amount) internal override {
    // Don't allow to withdraw max (reserved with withdrawAll call)
    if (_amount == type(uint256).max) revert InvalidArg();

    // Call withdraw with underlying amount of tokens (USDC instead of eUSDC)
    // https://github.com/euler-xyz/euler-contracts/blob/master/contracts/modules/EToken.sol#L177
    EUSDC.withdraw(SUB_ACCOUNT, _amount);

    // Transfer USDC to core
    want.safeTransfer(core, _amount);
  }
```

note that the _amount is passed as parameter and this _amount is the amount of token that is transferred 

as shown

```solidity
 want.safeTransfer(core, _amount);
```

however, the _amount that is passed as parameter may not be the amount that we withdraw.

In withdraw logic withdraw fund from the implementation in EToken below

https://github.com/euler-xyz/euler-contracts/blob/dfe600640e5e7a2eae1c26b768bbc1141bb4c9b9/contracts/modules/EToken.sol#L178

```solidity
        (amount, amountInternal) = withdrawAmounts(assetStorage, assetCache, account, amount);
        require(assetCache.poolSize >= amount, "e/insufficient-pool-size");

        pushTokens(assetCache, msgSender, amount);
```

note the important function

https://github.com/euler-xyz/euler-contracts/blob/dfe600640e5e7a2eae1c26b768bbc1141bb4c9b9/contracts/BaseLogic.sol#L391

```solidity
 withdrawAmounts(assetStorage, assetCache, account, amount);
```

the implementation is 

```solidity
    function withdrawAmounts(AssetStorage storage assetStorage, AssetCache memory assetCache, address account, uint amount) internal view returns (uint, uint) {
        uint amountInternal;
        if (amount == type(uint).max) {
            amountInternal = assetStorage.users[account].balance;
            amount = balanceToUnderlyingAmount(assetCache, amountInternal);
        } else {
            amount = decodeExternalAmount(assetCache, amount);
            amountInternal = underlyingAmountToBalanceRoundUp(assetCache, amount);
        }

        return (amount, amountInternal);
    }
```

the important function is 

https://github.com/euler-xyz/euler-contracts/blob/dfe600640e5e7a2eae1c26b768bbc1141bb4c9b9/contracts/BaseLogic.sol#L308

```solidity
     function balanceToUnderlyingAmount(AssetCache memory assetCache, uint amount) internal pure returns (uint) {
        uint exchangeRate = computeExchangeRate(assetCache);
        return amount * exchangeRate / 1e18;
    }
```

the implementation above means the amount of token withdraw is affected by the exchange rate.

For example, 

given the implementation

```solidity
 (amount, amountInternal) = withdrawAmounts(assetStorage, assetCache, account, amount);
```

the we passed in amount 100, but the function above returns amount 110
amount 110 is the actually amount that is withdraw.

however, only 100 amount of token is transferred into the Core contract.

## Impact

The user may withdraw the amount of token less than they expected.

## Code Snippet

## Tool used

Manual Review

## Recommendation

We recommend the project check the balance of the token in the contract
after withdraw and then transfer the token into the core contract as shown below

```solidity
  function _withdraw(uint256 _amount) internal override {
    // Don't allow to withdraw max (reserved with withdrawAll call)
    if (_amount == type(uint256).max) revert InvalidArg();

    // Call withdraw with underlying amount of tokens (USDC instead of eUSDC)
    // https://github.com/euler-xyz/euler-contracts/blob/master/contracts/modules/EToken.sol#L177
    EUSDC.withdraw(SUB_ACCOUNT, _amount);
    
    amount = want.balanceOf(address(this));
    // Transfer USDC to core
    if (amount != 0) want.safeTransfer(core, amount);
  }
```
