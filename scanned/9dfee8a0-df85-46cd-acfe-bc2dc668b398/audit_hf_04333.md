# [M] M-09 | Initial Deployed Liquidity Missing Crucial Validations

## Summary
Severity: Medium
Contest weight: 0.1394
Dataset id: 21489
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
For the V2 migration, the InitializeProtocol policy will be used. This will initialize the pool, mint the initial spot supply, setup credits and deploy the pool liquidity. The issue relies on the deployLiquidity function, as it only verifies the new deployed capacity is above the initial circulating supply. The missing validations are: • Verify the new liquidityD is not above MAX_DISCOVERY_RATIO, as the tick premium and leverage can be high. • Validate the spot supply is already minted, as the system might be insolvent and distributeSpot does not check this. • Validate credit is already setup, similar to spot, circulating supply will be minted and can make the system insolvent. Although there is some documentation about the steps for the V2 migration, the code does not enforce these steps, so there could be arbitrage attacks that can be triggered if the liquidity is not setup correctly.

## Recommendation
Check if the liquidity structure does not allow bump to be executed right away. Additionally, consider adding checks to ensure no more circulating supply is minted after the deployLiquidity is executed.
