# [H] ArrakisMetaVaultPrivate::fund No slippage con-

## Summary
Severity: High
Contest weight: 0.3707
Dataset id: 22828
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
An attacker can front-run a deposit transaction for an ArrakisMetaVaultPrivate, forcing the depositor to deposit in an unbalanced way. This increases liquidity around an unfavorable price, leading to a loss of one side of the provided liquidity.
The owner of a private vault has full ownership of the shares of liquidity, so they are not even calculated explicitly. It is thus not possible to quantify the slippage control as a minimum amount of shares minted.
However, by providing liquidity around an unfavorable price, the owner of the vault exposes one side of his liquidity to be backrun, as we will see in the concrete example below.
An attacker can manipulate the price at which liquidity is added, leading to potential losses for the depositor.

## Proof of Concept
To simulate the scenario, we use the Python script from the uniswapv3book
Scenario
Initial Pool State
• DAI is trading 1 : 1 to USDC.
• Price bounds set are: [0.5, 1.5].
• Reserves: 1000 USDC : 1000 DAI
• Liquidity: 3414
• Price: 1
Steps
1. Bob is a private vault owner and creates a tx to deposit 1000 USDC : 1000 DAI.
2. Alice front-runs Bob tx and swaps 1366 USDC for 975 DAI to decrease USDC price down to 0.51.
Pool State After Alice Front-runs
• Reserves: 2366 USDC : 25 DAI
• Liquidity: 3553
• Price: 0.51
3. Bob transaction goes through, he deposits 1000 USDC : 1000 DAI.
Pool State After Bob's Transaction
• Reserves: 3366 USDC : 1025 DAI
• Liquidity: 5765
• Price: 0.51
4. Alice back-runs Bob’s tx, and swaps 1647 DAI for 2307 USDC making a profit of 269 USDC.

## Recommendation
Enable private vault depositors to control deviation parameters exposed in HOT::depositLiquidity: _expectedSqrtSpotPriceLowerX96 and _expectedSqrtSpotPriceUpperX96 in ArrakisMetaVaultPrivate.sol::fund interface
