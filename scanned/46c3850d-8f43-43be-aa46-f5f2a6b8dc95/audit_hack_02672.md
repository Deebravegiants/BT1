# [H] withdraw reserved liquidity can fail when interacting with Premia Pool and revert the transaction when collecting performance fee and block the project from starting new epoch cycle and block withdraw from vault

## Summary
Severity: High
Reporter: ctf_sec
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L239
Type: audit-issue

## Details
# withdraw reserved liquidity can fail when interacting with Premia Pool and revert the transaction when collecting performance fee and block the project from starting new epoch cycle and block withdraw from vault

## Summary

WIthLiqudity can fail and revert the transaction when collecting performance fee and block the project from starting new auction cycle

## Vulnerability Detail

when the keepers calls the function initializeEpoch(), at first, the PerformanceFee is collected.

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L239

inside the function _collectPerformanceFee, we withdraw reserved liqudity

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultInternal.sol#L505-L508

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultInternal.sol#L538-L570

note the line 

```solidity
Pool.withdraw(reservedLiquidity, l.isCall); 
```

the external interaction can fail for a few reason:

1. insufficient liquidity in external pool.
2. the liqudity is locked because of the timelock

https://github.com/Premian-Labs/premia-contracts/blob/933575896b4d862de83d2a0a8f9f164655dd2b80/contracts/pool/PoolIO.sol#L98

the function below is comes from the PoolIO implementation from Premia option.

```solidity
    function withdraw(uint256 amount, bool isCallPool) public {
        PoolStorage.Layout storage l = PoolStorage.layout();
        uint256 toWithdraw = amount;

        _processPendingDeposits(l, isCallPool);

        uint256 depositedAt = l.depositedAt[msg.sender][isCallPool];

         require(depositedAt + (1 days) < block.timestamp, "liq lock 1d");
```

note the line

```solidity
  require(depositedAt + (1 days) < block.timestamp, "liq lock 1d");
```

we cannot withdraw liquidity after one day of the deposit time.

## Impact

the function _withdrawReservedLiquidity is used in function _withdraw and in _collectionPerformanceFee.

So if the external interaction revert, the project is not able to collection performance fee and start new epoch
and user is block from withdrawing their token.

## Code Snippet

## Tool used

Manual Review

## Recommendation

We recommend the project implement the smart contract such that the non-withdrawal liquidity can block user withdraw and new initialization of the epoch.
