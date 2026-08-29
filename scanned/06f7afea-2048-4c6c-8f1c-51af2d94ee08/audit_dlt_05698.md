# [H] ALCK rewards are lost when merging tokens becau...

## Summary
Severity: High
Chain: Smart contract
Component: Alchemix
Source: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/Alchemix/30826%20-%20%5BSC%20-%20High%5D%20ALCK%20rewards%20are%20lost%20when%20merging%20tokens%20becau....md
Type: immunefi-boost

## Details
Target: https://github.com/alchemix-finance/alchemix-v2-dao/blob/main/src/VotingEscrow.sol

## Description

## Brief/Intro

ALCK rewards are lost when merging tokens because the rewards are not claimed before burning the token.

## Vulnerability Details

Merging or withdrawing tokens require burning the token. When merging tokens, unclaimed rewards must be claimed before burning the token. This prevents users from losing their rewards when the tokens are burnt. This isn't the case however as unclaimed rewards are not claimed before burning the token. This makes the user's unclaimed ALCX rewards to become lost and unclaimable when the tokens are burnt.

```
        _checkpoint(_from, _locked0, LockedBalance(0, 0, false, 0));
        _burn(_from, value0);
        _depositFor(_to, value0, end, _locked1.maxLockEnabled, _locked1, DepositType.MERGE_TYPE);

```

In contrast to the merge function, the withdraw function first claims all unclaimed rewards before burning the token. This prevents users from losing their rewards when the tokens are burnt.

```
        // Claim any unclaimed ALCX rewards and FLUX
        IRewardsDistributor(distributor).claim(_tokenId, false);
        IFluxToken(FLUX).claimFlux(_tokenId, IFluxToken(FLUX).getUnclaimedFlux(_tokenId));

        // Burn the token
        _burn(_tokenId, value);
```

Hence, users will lose their ALCX rewards when merging tokens because the ALCX rewards are not claimed before burning the token. This leads to a permanent freezing of unclaimed rewards as the ALCX rewards are lost and unclaimable.

## Impact Details

Permanent freezing of unclaimed rewards

## References


_Trimmed to 38 lines — full report: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/Alchemix/30826%20-%20%5BSC%20-%20High%5D%20ALCK%20rewards%20are%20lost%20when%20merging%20tokens%20becau....md_
