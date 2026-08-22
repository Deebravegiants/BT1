# [M] User voting power is not synchronized after multiplier changes

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-arcade
Published: 2023-07-28
Source: https://github.com/code-423n4/2023-07-arcade-findings/issues/283
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-07-arcade/blob/main/contracts/NFTBoostVault.sol#L363-#L371


# Vulnerability details

## Impact
- User voting power is not synchronized after multiplier changes
- If manager decrease multiplier for a token, users voting power will not be affected

## Proof of Concept
Currently the function `setMultiplier` of contract `NFTBoostVault` is implemented as follows:
```solidity
    function setMultiplier(address tokenAddress, uint128 tokenId, uint128 multiplierValue) public override onlyManager {
        if (multiplierValue > MAX_MULTIPLIER) revert NBV_MultiplierLimit();

        NFTBoostVaultStorage.AddressUintUint storage multiplierData = _getMultipliers()[tokenAddress][tokenId];
        // set multiplier value
        multiplierData.multiplier = multiplierValue;

        emit MultiplierSet(tokenAddress, tokenId, multiplierValue);
    }
```

The problem with this code is that it does not update the users voting power, even though their multiplier has changed. The contract did provide a function called `updateVotingPower` to update users voting power as follows:
```solidity
    function updateVotingPower(address[] calldata userAddresses) public override {
        if (userAddresses.length > 50) revert NBV_ArrayTooManyElements();

        for (uint256 i = 0; i < userAddresses.length; ++i) {
            NFTBoostVaultStorage.Registration storage registration = _getRegistrations()[userAddresses[i]];
            _syncVotingPower(userAddresses[i], registration);
        }
    }
```
We can argue that the manager can call this function to update users voting power after they change multiplier; however, there are multiple problems with this solution:
- The input of `updateVotingPower` is a list of user adresses, so the manager must have map of token id to a list of users using that token id as their multiplier. However, this data is not saved in the contract. When users register, their registrations are tracked using a variable of type `map(address => NFTBoostVaultStorage.Registration)`. I've looked into the contracts and found no way to retrieve a list of users associated with a token id, even function `_registerAndDelegate` does not emit an event showing which ERC1155 tokenId the users use at registration time.

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-arcade-findings/issues/283_
