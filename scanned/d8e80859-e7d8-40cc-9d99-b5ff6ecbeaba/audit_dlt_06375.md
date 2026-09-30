# [H] `WiseSecurity.checksWithdraw` blocks the withdrawal of pooltokens

## Summary
Severity: High
Chain: Smart contract
Component: Wise-Lending
Published: 2024-02-18
Source: https://github.com/hats-finance/Wise-Lending-0xa2ca45d6e249641e595d50d1d9c69c9e3cd22573/issues/51
Type: hats-finding

## Details
**Github username:** @@Tri-pathi
**Twitter username:** @0xTripathi
**Submission hash (on-chain):** 0xaeef6a4fbcffae319f105895faba81fad54fabc042ee949dd304433087d19b27
**Severity:** high

**Description:**
**Description**


`WiseSecurity.checksWithdraw` blocks the withdrawal of pooltokens  
which are uncollateralized , blacklisted and have OpenBorrowPosition.

**Attack Scenario**


**Attachments**

1. **Proof of Concept (PoC) File**

Before withdrawing Caller need to pass `checksWithdraw()` and some other  security  checks

```solidity
    function checksWithdraw(
        uint256 _nftId,
        address _caller,
        address _poolToken
    )
        external
        view
        returns (bool specialCase)
    {
        if (_checkBlacklisted(_poolToken) == true) {

            if (overallETHBorrowBare(_nftId) > 0) {
                revert OpenBorrowPosition();
            }

            return true;
        }

        if (WISE_LENDING.verifiedIsolationPool(_caller) == true) {
            return true;
        }

        if (WISE_LENDING.positionLocked(_nftId) == true) {
            return true;
        }

        if (_isUncollateralized(_nftId, _poolToken) == true) {
            return true;
        }

        if (WISE_LENDING.getPositionBorrowTokenLength(_nftId) == 0) {
            return true;
        }
    }
```
https://github.com/wise-foundation/lending-audit/blob/master/contracts/WiseSecurity/WiseSecurity.sol#L237

If `poolToken` is blacklisted and uncollateralized they should be withdrawable even if there is OpenBorrowPosition. 
But here in this case withdrawl will revert with `OpenBorrowPosition()` and user's funds will be locked 

The oos text in contest page `In case of withdrawing an uncollateralized asset if you happen to be above 95% debtratio anyway it will still fail (only then). Being above 95% basically means you are in liquidation mode and are therfore incentivized to to use your uncollateralized as collateral instead of removing it to save money and avoid liquidation` It basically says that caller should first improve their borrow position and then withdraw 

But Here it's not the case as if pooltoken is blacklisted then uncollateralized pooltokens can't be used as a collateral to improve the borrow position. 

So all uncollateralized funds will stuck in the contract 

Why this is a issue ?

1) 

```solidity
    function revokeShutdown()
        external
        onlyMaster
    {
        _setPoolState(
            false
        );
    }


```

All other active user's who have uncollateralized assets could front run blacklisting and withdraw all their uncollateralized tokens since protocol allows to withdraw uncollateralized assets if its not blacklisted 
But funds will stuck for other people who wasn't able to front run


2)   Preventing them from withdrawing had a purpose so that they can first improve their borrow position and then withdraw to save their assets. But for blacklisted pooltokens uncollateralized assets can't be used so it doesn't make any sense to lock them.

Mayebe after withdrawl they can swap their withdrawl assets to borrowtoken and then repay borrow tokens to improve their position


User funds is locked here so marking as HIGH
