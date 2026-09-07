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
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Wise-Lending-0xa2ca45d6e249641e595d50d1d9c69c9e3cd22573/issues/51_
