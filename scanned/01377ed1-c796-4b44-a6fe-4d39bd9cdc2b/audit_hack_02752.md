# [M] User can still withdraw fund from the contract when admin paused EulerStragety.sol,

## Summary
Severity: Medium
Reporter: ctf_sec
Source: https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/EulerStrategy.sol#L51
Type: audit-issue

## Details
# User can still withdraw fund from the contract when admin paused EulerStragety.sol,

## Summary

User can't deposit fund into the underlying contract when paused from EulerStragety.sol, but user can withdraw fund from the contract when paused EulerStragety.sol

## Vulnerability Detail

note the implementation in the smart contract EulerStragety.sol

https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/EulerStrategy.sol#L51

```solidity
 function _deposit() internal override whenNotPaused
```

User can't deposit fund into the underlying contract when admin paused the contract.

but user can withdraw fund from the underlying contract when admin paused the contract,

there is no WhenNotPaused modifier in the withdraw function below

https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/EulerStrategy.sol#L59

https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/EulerStrategy.sol#L77

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

In extreme condition, the underlying contract may not have sufficient liquidity and withdraw will always fail, 
or the exchange rate changes dramatically and the withdrawal amount is less than what user expected.

in this case, it is ok to pause withdraw until the withdraw can be successfully called.

## Impact

When contract is paused, user can still withdraw their fund, result in user withdraw fund less than they expected
or the withdraw will always fail.

## Code Snippet

## Tool used

Manual Review

## Recommendation

We recommend adding WhenNotPaused function in the withdraw function

```solidity
 function _withdraw(uint256 _amount) internal WhenNotPaused override
```

```solidity
 function _withdrawAll() internal override WhenNotPaused returns (uint256 amount)
```
