# [M] Usage of malicious ERC20 contracts for DOS of various protocol functions

## Summary
Severity: Medium
Reporter: minhtrng
Source: https://github.com/sherlock-audit/2023-02-openq/blob/fc2dae7107e4be0878ace40b1e7218c18e1933fe/contracts/DepositManager/Implementations/DepositManagerV1.sol#L45-L56
Type: audit-issue

## Details
# Usage of malicious ERC20 contracts for DOS of various protocol functions

## Summary

Malicious ERC20 tokens added to a bounty can DOS various features, such as closing competitions or claiming funds.

## Vulnerability Detail

The function `DepositManager.fundBountyToken` allows for an arbitrary ERC20 token to be added to a bounty, as long as an address limit has not been reached:

```js
if (!isWhitelisted(_tokenAddress)) {
    require(
        !tokenAddressLimitReached(_bountyAddress),
        Errors.TOO_MANY_TOKEN_ADDRESSES
    );
}
...
(bytes32 depositId, uint256 volumeReceived) = bounty.receiveFunds{
    value: msg.value
}(msg.sender, _tokenAddress, _volume, _expiration);
```

In various places of the code, the whole set of added tokens is iterated over to call specific functions of the token contracts, some examples:

```js
//_claimAtomicBounty
for (uint256 i = 0; i < _bounty.getTokenAddresses().length; i++) {
    uint256 volume = _bounty.claimBalance(
        _closer,
        _bounty.getTokenAddresses()[i]
    );

//closeCompetition
for (uint256 i = 0; i < getTokenAddresses().length; i++) {
    address _tokenAddress = getTokenAddresses()[i];
    fundingTotals[_tokenAddress] = getTokenBalance(_tokenAddress);
}
```

This is easily DOSable by adding a malicious contract that reverts under certain conditions (e.g. switching a flag, so that the initial transfer in works, but no transfer outs after).

## Impact

DOS of key features such as claiming or closing competitions

## Code Snippet

https://github.com/sherlock-audit/2023-02-openq/blob/fc2dae7107e4be0878ace40b1e7218c18e1933fe/contracts/DepositManager/Implementations/DepositManagerV1.sol#L45-L56

https://github.com/sherlock-audit/2023-02-openq/blob/fc2dae7107e4be0878ace40b1e7218c18e1933fe/contracts/Bounty/Implementations/TieredPercentageBountyV1.sol#L132-L135

https://github.com/sherlock-audit/2023-02-openq/blob/fc2dae7107e4be0878ace40b1e7218c18e1933fe/contracts/ClaimManager/Implementations/ClaimManagerV1.sol#L130-L134

## Tool used

Manual Review

## Recommendation
There are different possible approaches with different pros and cons:

1. Only allow whitelisted tokens, but have an additional whitelist that only the bounty issuer can modify.
2. Instead of iterating over all the ERC20 tokens added to a list, allow the user of a function to pass a list of ERC20 tokens that he is interested in.
