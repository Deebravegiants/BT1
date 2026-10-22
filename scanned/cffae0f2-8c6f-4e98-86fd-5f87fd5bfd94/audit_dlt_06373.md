# [M] Multiple Collaterals powerFarm may be able to withdraw holding a blacklisted token

## Summary
Severity: Medium
Chain: Smart contract
Component: Wise-Lending
Published: 2024-02-19
Source: https://github.com/hats-finance/Wise-Lending-0xa2ca45d6e249641e595d50d1d9c69c9e3cd22573/issues/53
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x7c94d55332eb7982d1f529093b15584d101a8bb92cf98809defc152eb5022c54
**Severity:** medium

**Description:**
**Description**\
If powerFarm has at least 2 collaterals including a blacklisted token (or more if collaterals is = blacklisted + 1) and borrow doesnt include one you could theoretically withdraw a non blacklsted token from a position with open borrow since in healthstatecheck it calls if powerFarm true overallETHCollateralsBare

```

        uint256 overallCollateral = _powerFarm == true
            ? overallETHCollateralsBare(_nftId)
            : overallETHCollateralsWeighted(_nftId);

```

and this lacks _checkPoolCondition:

```
function overallETHCollateralsBare(
        uint256 _nftId
    )
        public
        view
        returns (uint256 amount)
    {
        address tokenAddress;

        uint256 i;
        uint256 l = WISE_LENDING.getPositionLendingTokenLength(
            _nftId
        );

        while (i < l) {

            tokenAddress = WISE_LENDING.getPositionLendingTokenByIndex(
                _nftId,
                i
            );

            amount += getFullCollateralETH(
                _nftId,
                tokenAddress
            );

            unchecked {
                ++i;
            }
        }
    }

```
Since if you call withdraw it checks if token is blacklisted this only works to withdraw a non blacklisted token while still holding a blacklisted token in the position too. This might be out of scope since you can just say powerFarms always have 1 collateral.

**Attack Scenario**\
Depending on why the token is blacklisted this could lead to bad debt etc.

**Attachments**

1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->

2. **Revised Code File (Optional)**
<!-- If possible, please provide a second file containing the revised code that offers a potential fix for the vulnerability. This file should include the following information:
- Comment with a clear explanation of the proposed fix.
- The revised code with your suggested changes.
- Any additional comments or explanations that clarify how the fix addresses the vulnerability. -->
