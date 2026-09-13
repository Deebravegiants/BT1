# [H] Portal can be rendered un-usable using a simple front-back-run of convert() calls

## Summary
Severity: High
Chain: Smart contract
Component: Possum-Labs--Portals-
Published: 2023-11-20
Source: https://github.com/hats-finance/Possum-Labs--Portals--0xed8965d49b8aeca763447d56e6da7f4e0506b2d3/issues/66
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x80d39c49bff626f3950c1082cd1b62073b02edba20303581614d864c537204a7
**Severity:** high

**Description:**
**Description**\
 When the portal launches, the initial price of PE to PSM is determined by _FUNDING_EXCHANGE_RATIO (550). this is a low starting point that is supposed to increase over time through calls to the convert() function, which add PSM to the portal and push the price of PE/PSM a little at a time until it roughly equates the value of Energy gained upfront from staking HLP to HLP's market staking interest. However, an exploiter can front+back run any call to convert() by buying PE before the convert and selling it immediately after. The exploiter does not need to stake anything themselves, other than a minimal amount to have an account in the system. As the POC shows, the exploiter can figure out the amounts of PSM buy/sell that will transfer almost all of the PSM added to the system by the convert() to the exploiter, leaving the price of the internal LP barely changed. If this is done consistantly, PE/PSM price never increases to the point of making a stake in Possum viable. Over time stakers will avoid staking in the portal, rending it useless. Note: this is not a fronttun to grief arbitrajeurs, in this scenario arbitrajeurs gain their expected profit. The exploited party are stakers that never get to see their gained energy accrue value.

**Attack Scenario**\
Exploiter opens an account by staking a very low amount (1 wei HLP), Eploiter front-runs any call to convert() with buyPortalEnergy (ideal quantity can be calculated as the POC shows), convert() is called, exploiter calls sellPortalEnergy, taking a profit of roughly the dollar value of 100,000 PSM and portal PE/PSM price remains the same never acrruing value

**Attachments**

1. **Proof of Concept (PoC) File**
See attached file with running instructions

2. **Revised Code File (Optional)**
Unfortunately no easy fix here since this touches on core mechanics. A possible solution could be to only allow buying portal energy from an account that has some minimal HLP stake (which might make this exploit non-profitable since the exploiter would also loose from their stake never accruing the market interest) however this requires further consideration of all sideeffects
  
**Files:**
  - possumPOC.sol (https://hats-backend-prod.herokuapp.com/v1/files/QmVgThZEfEqNoxV4QcPuCzEbP9B3828mrrjS7vATUaQd92)
