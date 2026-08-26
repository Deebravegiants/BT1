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
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Wise-Lending-0xa2ca45d6e249641e595d50d1d9c69c9e3cd22573/issues/53_
