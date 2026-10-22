# [M] getDeltaStrikePrice64x64() need sanity check

## Summary
Severity: Medium
Reporter: __141345__
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/pricer/Pricer.sol#L79-L105
Type: audit-issue

## Details
# getDeltaStrikePrice64x64() need sanity check

## Summary

Premia has a certain strike price range requirement, if the strike price derived from getDeltaStrikePrice64x64() is out of the range, the option can not be written. The auction has to be canceled. 


## Vulnerability Detail

If the strike price derived might be out of Premia's price range, the option will not be written, but revert at the end of the auction.

## Impact

Auction might be canceled at last. 
User fund will sit idle stop working and users lose the yield.



## Code Snippet

The is no strike bound check in `getDeltaStrikePrice64x64()`:
https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/pricer/Pricer.sol#L79-L105

Premia has a certain price range:
```solidity
// https://github.com/Premian-Labs/premia-contracts/blob/933575896b4d862de83d2a0a8f9f164655dd2b80/contracts/pool/PoolWrite.sol#L267-L290
    function _verifyPurchase(
        uint64 maturity,
        int128 strike64x64,
        bool isCall,
        int128 spot64x64
    ) internal view {
        require(maturity >= block.timestamp + (1 days), "exp < 1 day");
        require(maturity < block.timestamp + (91 days), "exp > 90 days");
        require(maturity % (8 hours) == 0, "exp must be 8-hour increment");

        if (isCall) {
            require(
                strike64x64 <= spot64x64 << 1 &&
                    strike64x64 >= (spot64x64 * 8) / 10,
                "strike out of range"
            );
        } else {
            require(
                strike64x64 <= (spot64x64 * 12) / 10 &&
                    strike64x64 >= spot64x64 >> 1,
                "strike out of range"
            );
        }
    }
```
## Tool used

Manual Review


## Recommendation

Add strike price bound check in `getDeltaStrikePrice64x64()`.
