# [H] Use can get unlimited votes

## Summary
Severity: High
Chain: Smart contract
Component: 2022-09-nouns-builder
Published: 2022-09-15
Source: https://github.com/code-423n4/2022-09-nouns-builder-findings/issues/469
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-09-nouns-builder/blob/7e9fddbbacdd7d7812e912a369cfd862ee67dc03/src/lib/token/ERC721Votes.sol#L268


# Vulnerability details

## Impact

`aftertokenTransfer` in ERC721Votes transfers votes between user addresses instead of the delegated addresses, so a user can cause overflow in `_moveDelegates` and get unlimited votes

## Proof of Concept

https://github.com/code-423n4/2022-09-nouns-builder/blob/7e9fddbbacdd7d7812e912a369cfd862ee67dc03/src/lib/token/ERC721Votes.sol#L268

```
    function _afterTokenTransfer(
        address _from,
        address _to,
        uint256 _tokenId
    ) internal override {
        // Transfer 1 vote from the sender to the recipient
        _moveDelegateVotes(_from, _to, 1);

        super._afterTokenTransfer(_from, _to, _tokenId);
    }
```
https://github.com/code-423n4/2022-09-nouns-builder/blob/7e9fddbbacdd7d7812e912a369cfd862ee67dc03/src/lib/token/ERC721Votes.sol#L216

```
    _moveDelegateVotes(prevDelegate, _to, balanceOf(_from));
    ...
    unchecked {
                ...
                // Update their voting weight
                _writeCheckpoint(_from, nCheckpoints, prevTotalVotes, prevTotalVotes - _amount);
            }
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2022-09-nouns-builder-findings/issues/469_
