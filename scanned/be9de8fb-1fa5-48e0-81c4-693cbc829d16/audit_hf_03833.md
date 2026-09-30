# [M] Market Allows Zero Amount Positions Which

## Summary
Severity: Medium
Contest weight: 0.1801
Dataset id: 20067
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When adjusting positions, it correctly calculates the amount and respects limits, but it runs into a problem when dealing with a zero amount in the openMake and closeMake functions. This problem occurs when the Vault doesn't wish to change any position but still communicates a "0" amount to the product, resulting in revert and halting the rebalancing process.

When decreasing a position, the Market Vault calculates the available room and permits only the closing of positions up to the point where the maker equals the taker. If the market's taker is greater than the maker, the amount is deemed as zero.
Conversely, when increasing a position, the Vault checks if the product's maker limit is exceeded. If it is, the Vault assigns the amount as zero. Following this, the Vault executes the closeMake and openMake functions using the calculated amount.

However, an issue arises with the Vault's openMake and closeMake functions operating with a zero amount. Even though the Vault might not want to open or close any position, it still calls the product with a "0" amount. This leads to the modifiers throwing an error, and the rebalancing process gets stuck.

In such cases where maker limit is exceeded in product or takers > makers vaults rebalancing will be stuck. Therefore, I'll call it as high

## Recommendation
If the calculated openMake/closeMake amount is "0" don't call the products functions. Just exit the function.
