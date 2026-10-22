# [H] safeMint() does not check the parameter "tokenId"

## Summary
Severity: High
Reporter: BugHunter101
Source: https://github.com/sherlock-audit/2023-04-footium/blob/main/footium-eth-shareable/contracts/FootiumClub.sol#L56
Type: audit-issue

## Details
# safeMint() does not check the parameter "tokenId"

## Summary

The function safeMint() does not check the parameter "tokenId", if may causes clubToEscrow to repeat.

## Vulnerability Detail

The function safeMint() does not check the parameter "tokenId", if may causes clubToEscrow to repeat.

## Impact

cause the function to be invalid

## Code Snippet

https://github.com/sherlock-audit/2023-04-footium/blob/main/footium-eth-shareable/contracts/FootiumClub.sol#L56

function safeMint(address to, uint256 tokenId)
        external
        onlyRole(MINTER_ROLE)
        nonReentrant
        whenNotPaused
    {
        FootiumEscrow escrow = new FootiumEscrow(address(this), tokenId);
        clubToEscrow[tokenId] = escrow;

        _mint(to, tokenId);

        emit EscrowDeployed(tokenId, escrow);
    }

## Tool used

Manual Review

## Recommendation

check the parameter "tokenId"
