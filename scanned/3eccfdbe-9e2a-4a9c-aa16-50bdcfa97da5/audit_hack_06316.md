# [M] Refunds can be disabled with dust deposits

## Summary
Severity: Medium
Reporter: minhtrng
Source: https://github.com/sherlock-audit/2023-02-openq/blob/fc2dae7107e4be0878ace40b1e7218c18e1933fe/contracts/Bounty/Implementations/BountyCore.sol#L340-L349
Type: audit-issue

## Details
# Refunds can be disabled with dust deposits

## Summary

Refunds can be DOSed by performing a lot of dust deposits. 

## Vulnerability Detail

The function `BountyCore.getLockedFunds` iterates over the unbounded length of deposits to determine the token amount that is past expiration:

```js
bytes32[] memory depList = this.getDeposits();
for (uint256 i = 0; i < depList.length; i++) {
    if (
        block.timestamp <
        depositTime[depList[i]] + expiration[depList[i]] &&
        tokenAddress[depList[i]] == _depositId
    ) {
        lockedFunds += volume[depList[i]];
    }
}
```

This function is used within `DepositManager.refundDeposit` to determine the available funds:

```js
uint256 availableFunds = bounty.getTokenBalance(depToken) -
    bounty.getLockedFunds(depToken);
```

The deposit list can be increased arbitrarily by calling `DepositManager.fundBountyToken` with a tiny amount for the `volume` parameter. Once the list has gotten large enough, the `refundDeposit` function will run out of gas when trying to execute.


## Impact

DOS of refunds possible for any token.

## Code Snippet

https://github.com/sherlock-audit/2023-02-openq/blob/fc2dae7107e4be0878ace40b1e7218c18e1933fe/contracts/Bounty/Implementations/BountyCore.sol#L340-L349

## Tool used

Manual Review

## Recommendation

Limit the number of deposits (similar as is the intention behind the tokenAddressLimit) or have a minimum deposit size determined by the issuer (difficult to realize, since any token contract is meant to be supported)
