# [M] In PriceTierVesting there is no check if the Se-

## Summary
Severity: Medium
Contest weight: 0.1302
Dataset id: 20237
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Price from oracle on L2s can be invalid/stale if the sequencer is down. This could lead to users being able to claim tokens that they should not be able to claim. If the sequencer of the L2s were to go offline the Chainlink oracle may return an invalid/stale price. This could lead to users being able to claim tokens that they should not be able to claim. tier price, this would have unlocked all tokens to be claimable. If the sequencer the oracle would still return the high price even though the price is lower now and not all tokens should be claimable. It should always be checked if the sequencer is up before consuming any data from Chainlink. For more details on L2 Sequencer Uptime Feeds check the Chainlink docs(https://docs.chain.link/data-feeds/l2-sequencer-feeds) specify more details. Receivers can claim tokens they should not be able to claim

## Recommendation
Include a check if the sequencer is up. If it is down, revert when calling getVestedFraction in PriceTierVesting
