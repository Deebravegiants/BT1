# [H] `LM_PC_Bounties_v1::contributorsNotChanged`check is not enough, could result in CLAIMANT adding additional contributors in the last minute

## Summary
Severity: High
Chain: Smart contract
Component: Inverter-Network
Published: 2024-06-09
Source: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/82
Type: hats-finding

## Details
**Github username:** @NicolaMirchev
**Twitter username:** EgisSec
**Submission hash (on-chain):** 0xf81483741acb09b3f2c39da0a278fc725098b2e97ff457a40d5a166533fe3699
**Severity:** high

**Description:**
**Description**\
Inside [LM_PC_Bounties_v1](https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/blob/09e3a91bdc298a8666f666efbce408178cd83ec8/src/modules/logicModule/LM_PC_Bounties_v1.sol#L45) there are multiple roles responsible for paying out bounties to contributors to ensure better transparency and decentralization. [BOUNTY_ISSUER_ROLE](https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/blob/09e3a91bdc298a8666f666efbce408178cd83ec8/src/modules/logicModule/LM_PC_Bounties_v1.sol#L295-L304) is responsible for adding bounty config. Next step is [CLAIMANT_ROLE](https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/blob/09e3a91bdc298a8666f666efbce408178cd83ec8/src/modules/logicModule/LM_PC_Bounties_v1.sol#L349-L359) to configure contributors array with valid contributors addresses and amounts to be claimed. Last step is [VERIFIER_ROLE](https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/blob/09e3a91bdc298a8666f666efbce408178cd83ec8/src/modules/logicModule/LM_PC_Bounties_v1.sol#L444-L450) to trigger the payment processing to contributors, providing. He is providing `contributors` array to be checked against  earlier configured by `CLAIMANT`. The problem here is that verifier provided `contributors`array length is not checked against `_claimRegistry[claimId].contributors`. It is only checking that elements elements  until `contributors[contributors.length - 1]` match those inside `_claimRegistry[claimId].contributors` until the same index:
```
    function contributorsNotChanged(
        uint claimId,
        Contributor[] memory contributors
    ) internal view {
        Contributor[] memory claimContribs =
            _claimRegistry[claimId].contributors;

        uint length = contributors.length;
        for (uint i; i < length;) {
            if (
                contributors[i].addr != claimContribs[i].addr
                    || contributors[i].claimAmount != claimContribs[i].claimAmount
            ) revert Module__LM_PC_Bounty__ContributorsChanged();
            unchecked {
                i++;
            }
        }
    }
```
The problem is that claimant may [updateClaimContributors](https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/blob/09e3a91bdc298a8666f666efbce408178cd83ec8/src/modules/logicModule/LM_PC_Bounties_v1.sol#L390-L399) adding new contributors in the end of the array right befor verifier calling `verifyClaim` with old `contributors` array. This would result in transferring payments to more addresses than the verifier intended. 

**Attack Scenario**\
Imagine the following scenario:


1. There is an active bounty program.
2. A bounty is opened for paying out developers who have contributed to some project.
3. Owner of the bounty loves the idea of decentralization and have configured different actors addresses for different roles.
4. Bounty is configured and `CLAIMENT` set `_claimRegistry[claimId].contributors` to addresses of 5 developers, who has worked with each `amount = 1000 USDC`, where maxBounty = `10 000 USDC` 

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/82_
