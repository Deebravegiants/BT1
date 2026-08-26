# [H] Portal Ignores Principal Token and PSM Price Ratio

## Summary
Severity: High
Chain: Smart contract
Component: Possum-Labs--Portals-
Published: 2023-11-18
Source: https://github.com/hats-finance/Possum-Labs--Portals--0xed8965d49b8aeca763447d56e6da7f4e0506b2d3/issues/49
Type: hats-finding

## Details
**Github username:** @0xmahdirostami
**Twitter username:** 0xmahdirostami
**Submission hash (on-chain):** 0x01dd911fdbaddd77f27734b310017dba8ff282920fcde96fd57a222410e1b304
**Severity:** high

**Description:**
**Description**\

The current implementation of the portal does not consider the price ratio between the principal token and PSM when calculating portal energy. This can lead to a situation where the yield is significantly less compared to the staked amount, especially when the PSM price is lower than the principal token price.

Picture this: currently PSM price is 0.001, and HLP price is 1.02. If a user deposits 1000e18 HLP, they'll get around 250e18 energy. Now, the energy converts to PSM at a rate of 550:1, so they end up with nearly 5e17 PSM tokens, valued at 0.0005.

**Impact**\
The current implementation may result in users receiving less yield than expected, causing a discrepancy between the staked amount and the obtained yield

**Attachments**

1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->

2. **Revised Code File (Optional)**
<!-- If possible, please provide a second file containing the revised code that offers a potential fix for the vulnerability. This file should include the following information:
- Comment with a clear explanation of the proposed fix.
- The revised code with your suggested changes.
- Any additional comments or explanations that clarify how the fix addresses the vulnerability. -->
Suggested fix: Consider both the principal token price and PSM price when using the _FUNDING_EXCHANGE_RATIO.
