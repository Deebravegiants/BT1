# [M] LP tokens from Boosted Positions are not included in the TVL calculation of a position held by the MaverickConnector 

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-noya
Published: 2024-05-17
Source: https://github.com/code-423n4/2024-04-noya-findings/issues/1263
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/connectors/MaverickConnector.sol#L153-L159


# Vulnerability details

## Impact

Because LP tokens from Boosted Positions are not included in the TVL calculation of a position held by the MaverickConnector, the calculated position TVL will be lower than the actual position TVL. This will result in a lower TVL for the associated vault. Therefor users who withdraw from the corresponding vault will get less value than they should be getting. Also, users who deposit to the vault will get more vault shares minted to them than they should be getting.


## Proof of Concept
 
Some liquidity pools in the Maverck protocol have so called boosted positions (BP) which are incentivised by additional rewards. To get these rewards the MaverickConnector must supply tokens to the BP and stake the LP tokens from the supply in the corresponding reward contract.

In contrast to normal positions which are represented by an NFT, the assets deposited into BP are represented by LP tokens. 

When calling `_getPositionTVL` to calculate the TVL of a position held by the MaverickConnector, only the assets represented by NFTs are considered by calling `addressBinReservesAllKindsAllTokenIds` and assets from BP represented by LP tokens are ignored. 

This means that the calculated TVL of the position and therefore the calculated TVL of the corresponding vault will be lower than the actual TVL.
 
The calculated TVL of a vault is the basis to determine how much value a user gets when withdrawing shares from the vault. E.g. if a user redeems 10% of all vault shares he will get 10% of the calculated TVL. Since the calculated TVL of the vault is lower than the actual vault TVL, any user who withdraws from the vault will receive less value for his shares than he should be receiving.

The calculated vault TVL is also used to determine how many shares a user gets when depositing to the vault. This is done by multiplying the value the user wants to supply with the outstanding shares of the vault and dividing it by the calculated TVL. Since the calculated TVL is lower than the actual TVL, users depositing to the vault will get more share minted to them than they should be getting.


## Recommended Mitigation Steps

Make sure to account for the tokens represented by LP token of BP when calculating the TVL of a position. The documentation on how to do this can be found [here]( https://docs.mav.xyz/v1-technical-reference/finding-lp-balances#id-2.-lp-balances-in-boosted-positions-unstaked). Make sure to implement both look ups for unstaked LP tokens and staked LP tokens.



## Assessed type

Invalid Validation
