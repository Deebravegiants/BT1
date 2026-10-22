# [M] A user is able to mint all or a large amount of nfts for themselves in a single transaction

## Summary
Severity: Medium
Reporter: dipp
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L161-L165
Type: audit-issue

## Details
# A user is able to mint all or a large amount of nfts for themselves in a single transaction

## Summary

A user could mint all or a majority of nfts in a single transactions using mutiple addresses/contracts preventing other users from having a chance to mint nfts.

## Vulnerability Detail

If a user overpays in the ```mint``` function the overpayed amount is refunded using a ```call```. 

[code:](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L161-L165)
```solidity
        if(msg.value > totalPaid) {
            // If too much ETH was sent, refund the difference
            (bool success, ) = payable(msg.sender).call{value: msg.value - totalPaid}(bytes(""));
            require(success, "Refund failed");
        }
```

The caller/user's receive function is then triggered. The receive function could call another contract to mint more nfts and overpay so that its receive function is called as well which leads to a chain of contracts minting the nfts in a single transaction. The user could mint all or a large portion of the nfts in a single transaction without giving other users a chance.

## Impact

The ```mintedPerAddress``` limits the amount of nfts a single address is able to mint. Although ```mintedPerAddress``` does not prevent a user from minting nfts with multiple addresses, it should still allow other users chances to front run and mint for themselves. This issue could allow a single user using multiple contracts/addresses to mint the majority of nfts without allowing other users a fair chance.



## Code Snippet

[MeritDutchAuction.sol#L128-L169](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128-L169)

## Tool used

Manual Review

## Recommendation

Only allow msg.value == totalPaid or track the amount to refund a user and them ouside of the mint function.
