# [M] Should prevent users from sending more native tokens

## Summary
Severity: Medium
Reporter: Bnke0x0
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/Auction.sol#L400-L403
Type: audit-issue

## Details
# Should prevent users from sending more native tokens

## Summary
Should prevent users from sending more native tokens

## Vulnerability Detail

## Impact
When a user bridges a native token  In other words, if a user accidentally sends more native tokens than he has to, the contract accepts it but only bridges, The rest of the tokens are left in the contract and can be recovered by anyone 

## Code Snippet
1. Fille: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/Auction.sol#L400-L403

       'require(
                longTokenBalance >= totalContractsSold,
                "long tokens not transferred"
            );'

2. Fille: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L636-L638

       ' amountCredited >= s.amountOutMin,
            "not enough output from trade"
        );'


3. Fille: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/QueueInternal.sol#L247-L250

       ' amountCredited >= s.amountOutMin,
            "not enough output from trade"
        );'

4. Fille: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultInternal.sol#L245-L248

       ' require(
                allowance >= shareAmount,
                "ERC4626: share amount exceeds allowance"
            );'

## Tool used

Manual Review

## Recommendation
1.  the provided native token is ensured to be the exact bridged amount, which effectively prevents the above scenario of loss of funds.
2. Consider changing '>=' to '=='

1. Fille: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/Auction.sol#L400-L403

       'require(
                longTokenBalance == totalContractsSold,
                "long tokens not transferred"
            );'

2. Fille: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L636-L638

       ' amountCredited ==s.amountOutMin,
            "not enough output from trade"
        );'


3. Fille: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/QueueInternal.sol#L247-L250

       ' amountCredited == s.amountOutMin,
            "not enough output from trade"
        );'

4. Fille: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultInternal.sol#L245-L248

       ' require(
                allowance == shareAmount,
                "ERC4626: share amount exceeds allowance"
            );'
