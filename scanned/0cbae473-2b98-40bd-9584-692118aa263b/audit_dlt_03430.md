# [M] In the BalancerConnector, unclaimed rewards are not included in the calculation of the connectors TVL

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-noya
Published: 2024-05-17
Source: https://github.com/code-423n4/2024-04-noya-findings/issues/1402
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/connectors/BalancerConnector.sol#L162-L173


# Vulnerability details

## Impact

Because unclaimed rewards are not included in the calculation of the TLV position held by the BalancerConnector, the calculated position TVL will be lower than the actual position TVL. This will result in a lower TVL for the associated vault. Therefor users who withdraw from the corresponding vault will get less value than they should be getting. Also, users who deposit to the vault will get more vault shares minted to them than they should be getting.



## Proof of Concept
 

In the Balancer protocol, users can earn rewards by depositing their LP tokens in the AuraPool. 
 
The issue arises from the fact that unclaimed rewards are not included in the calculation of the positions TVL. This means that the calculated TVL of the position and therefore the calculated TVL of the corresponding vault will be lower than the actual TVL. 
The calculated TVL of a vault is the basis to determine how much value a user gets when withdrawing shares from the vault. E.g. if a user redeems 10% of all vault shares he will get 10% of the calculated TVL. Since the calculated TVL is lower than the actual TVL, any user who withdraws from the vault will receive less value for his shares than he should be receiving.

The calculated TVL is also used to determine how many shares a user gets when depositing to the vault by multiplying the value the user wants to supply with the outstanding shares and dividing it by the calculated TVL. Since the calculated TVL is lower than the actual TVL, users depositing to the vault will get more share minted to them than they should be getting.



## Recommended Mitigation Steps

When calculating the TVL of a position held by the BalancerConnector, make sure to include the unclaimed rewards. For this get the amount of unclaimed tokens, determine the value of the rewards by calling `_getValue` for the reward tokens and add the value to the returned TVL of the position.



## Assessed type

Other
