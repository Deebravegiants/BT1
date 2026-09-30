# [M] Lack of slippage parameters on deposits

## Summary
Severity: Medium
Contest weight: 0.2331
Dataset id: 22914
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The lack of slippage parameters on deposits will allow minting fewer shares than expected if prices have changed between the time the user sends the transaction and when the transaction gets included in a block. When a user makes a deposit in a Vault, the _depositFor first calculates the amount in USD that represents that deposit. Then, it uses a formula to calculate the shares to mint for that user making the deposit:  
liquidityMinted := usdAmount \* totalSupply / totalAssets \* (1 - entryFee)  
*The names of the variables may be different on the code but the underlying formula is the same. Just to clarify, usdAmount represents the deposit value in USD, and totalAssets represent the total value of the Vault in USD. In the period between the user submitting a deposit transaction and that transaction getting included in a block, the prices could change and that can cause the user to receive fewer shares than expected. For example, when a Vault uses different tokens to deposit and to invest, it's possible that a change in value on one of those tokens will alter the shares minted to a user. Imagine a Vault has almost all the assets invested in ETH and they accept stablecoins as deposit assets. In that case, if the price of ETH suddenly rises when the deposit transaction is still pending, the value of totalAssets will be bigger, thus resulting in a lower value for liquidityMinted. Another example is if a Vault has almost all the assets in stablecoins and accepts ETH as a deposit asset, a sudden fall of the ETH price while a deposit transaction is pending will cause the minting of fewer shares than expected. In this case, the value of usdAmount will be lower, resulting in fewer shares minted. Users depositing into Vaults will receive fewer shares than expected, thus causing a loss of funds.

## Recommendation
To mitigate this issue is recommended to add a slippage parameter to all deposit functions so that a user can make a transaction revert if the received shares are less than expected.
