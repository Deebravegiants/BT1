# [H] Lack of yield token validation can lead to loss of funds

## Summary
Severity: High
Contest weight: 0.2560
Dataset id: 4214
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The createRedemption function in Transmuter does not validate whether the yieldToken provided by the user is actually associated with the specified alchemist. Additionally, during redemption, there is no such validation either. ITransumter.createRedemption is specified to take underlying as an input parameter. The assumption that all underlying assets are worth the same and should convert at a 1:1 exchange rate might be correct. However, the actual implementation allows users to provide a yieldToken instead of underlying, and different yieldTokens do not have the same value. An attacker can exploit this by: 1. Creating a redemption request using an alchemist associated with a lower-value yieldToken but inputting a more valuable yieldToken in the function arguments. 2. During redemption, calculations are performed based on the cheaper yieldToken, but the attacker ultimately receives the more valuable token, leading to a loss for the protocol. Additionally, the provided yieldToken can be an attacker-controlled ERC20 token, potentially allowing re-entrancy or manipulation via balanceOf calls.

## Recommendation
Ensure that the yieldToken provided by the user is explicitly associated with the specified alchemist.
