# [M] `CAP_PER_ADDRESS` not enforced

## Summary
Severity: Medium
Reporter: Czar102
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L12
Type: audit-issue

## Details
# `CAP_PER_ADDRESS` not enforced

## Summary
The cap per address for minting tokens is not enforced – an address may effectively mint more tokens. Hence, core protocol functionality is impaired. It cannot be fixed by redeploying, since the tokens have already been minted in the ERC721 contract.

## Vulnerability Detail
Because anyone can create as many identities on EVM chains, the cap per address can be easily bypassed.

For example, in case of a contract, it may deploy proxies that buy `CAP_PER_ADDRESS` tokens each and then send those to the owner contract and then selfdestruct. The state change is effectively the same as if the core contract bought more than `CAP_PER_ADDRESS` tokens.

## Impact
The cap per address is not enforced. Identities may effectively mint more tokens.

## Code Snippet
```js
        // Cannot mint more than the cap per address
        require(mintedPerAddressBefore + amount <= CAP_PER_ADDRESS, "Mint cap per address reached");
```

## Tool used

Manual Review

## Recommendation
To limit the number of tokens that can be minted by someone, another identity than an address needs to be used. Or, alternatively, one can use a whitelist for determining addresses that can mint up to [`CAP_PER_ADDRESS`](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L12) tokens.
