# [C] C-02 | Floor Inflation Allows Risk Free Shorts

## Summary
Severity: Critical
Contest weight: 0.2906
Dataset id: 21491
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the slide function the amount of liquidity credited to the floor range is dependent on the balance of the BPOOL contract after allocating the discovery and anchor positions. Users who hold a large amount of bAssets can game this behavior for an immediate and significant gain in their bAsset amount. Consider the following scenario: A Whale user starts at price A and sells bAssets to move price into the floor at price B. The user then maliciously sends reserve tokens directly to the BPOOL contract and triggers a slide. During the slide the reserve tokens sent this way are attributed to the liquidity of the floor. However since price is inside of the floor, these bAssets are "leveraged" as for the reserve tokens deployed to the floor position, there are corresponding bAssets which are minted to be paired. Now using the increased "leveraged" liquidity in the floor position, the user swaps all of the remaining reserves they had received from the original sell. Only now, due to the increased liquidity of the floor, they only reach C as a final price on their buy. This way the user's average price on the buy is much lower than the average price on their sell, and they realize an immediate arbitrage profit in terms of bAssets, this guarantees profit on a bAsset short.

## Recommendation
Burn any assets in the BPOOL prior to removing the three positions from the liquidity pool, this way malicious actors cannot tamper with the resulting liquidity amounts in the floor position and create profitable scenarios.
