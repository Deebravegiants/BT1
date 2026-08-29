# [M] collateralizeDeposit doesnt check for blacklist property

## Summary
Severity: Medium
Chain: Smart contract
Component: Wise-Lending
Published: 2024-02-19
Source: https://github.com/hats-finance/Wise-Lending-0xa2ca45d6e249641e595d50d1d9c69c9e3cd22573/issues/52
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x2856dfc178743b0a4b304d133567683c6979ad0e1a2aabe6f38f0e56493a10ff
**Severity:** medium

**Description:**
**Description**\
In 
```
function checksCollateralizeDeposit(
        uint256 _nftId,
        address _caller,
        address _poolAddress
    )
        external
        view
    {
        if (checkHeartbeat(_poolAddress) == false) {
            revert ChainlinkDead();
        }

        checkOwnerPosition(
            _nftId,
            _caller
        );
    }

```
Here a blacklisted token check needs to be added.
Incentive is to get rid of blacklist tokens not add them as collateral.

**Attack Scenario**\
1.) Collateralizing a blacklisted token blocks future borrow and withdraw capabilities
 

**Attachments**

1. **Proof of Concept (PoC) File**

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Wise-Lending-0xa2ca45d6e249641e595d50d1d9c69c9e3cd22573/issues/52_
