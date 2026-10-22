# [M] Enigma Vault Does Not Work With Fee-On-Transfer Tokens

## Summary
Severity: Medium
Contest weight: 0.1690
Dataset id: 15617
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Currently, the contract is not compatible with tokens that have a fee-on-transfer. This problem affects not only the deposit function, where users might receive more shares than the actual number of tokens received by the Enigma Vault but also poses a problem for the withdrawal function.

It could lead to fund loss if a token with a fee-on-transfer mechanism is used and not properly handled in Enigma Vault, it can result in stuck balances of this token of users. Such tokens for example are PAXG, while USDT has a built-in fee-on-transfer mechanism that is currently switched off.

Attack Scenario

1. Alice attempts to withdraw 10,000e18 shares from the vault using the withdraw() function.

2. The strategy separates the corresponding amount of liquidity tokens into token0 and token1.

3. The vault initiates a transfer of the respective amount0 and amount1 from the strategy contract to the user. However, if the tokens include a fee on transfer, there’s a possibility that the strategy might not have enough tokens to complete the transfer.

4. Due to the shortfall in tokens caused by the transfer fee, the withdraw function ultimately fails and reverts.

## Recommendation
As the protocol is intended to support any ERC20 token, it is recommended to check the balance before and after the transfer and validate if the result is the same as the amount argument provided.
