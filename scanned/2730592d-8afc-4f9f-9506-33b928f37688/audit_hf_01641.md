# [C] Frontrunning Pool Initialization Enables Price Manipulation Attack During Liquidity Migration

## Summary
Severity: Critical
Contest weight: 0.5526
Dataset id: 8792
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When the HotCurves contract's internal calculation of market cap exceeds the finalMarketCap, the function finalize() is triggered. Within finalize(), a Uniswap V3 pool for (HotKey, Token) is created and initialized if it does not already exist, using createAndInitializePoolIfNecessary(). However, if an attacker has preemptively created and initialized that pool at a highly skewed price, the contract will not overwrite the attacker's price. After detecting the pool is already initialized, the contract simply calls mintPosition() to provide all of its HotKey and Token liquidity with no price or slippage checks (amount0Min = 0 and amount1Min = 0). As a result, the skewed price set by the attacker remains in place, causing the contract to deposit liquidity at an extremely unfavorable ratio.

## Proof of Concept
no poc (PoC) here  
1. The attacker observes that the market cap is approaching the threshold of 11.5 ETH, which triggers finalize().  
2. The attacker notices that upcoming buy transactions will push the market cap from 11.49 ETH to 11.51 ETH, surpassing the 11.5 ETH threshold and triggering finalize().  
3. Before the contract reaches this threshold, the attacker manually deploys a (hotKey, Token) pool on Uniswap V3 with a 1% fee tier (fee = 10,000). However, instead of setting a fair price (e.g., 1 hotKey = 1 Token), they initialize the pool with an extreme skew: 1 Token = 1e18 hotKey.  
- To achieve this, the attacker calls the Uniswap V3 Factory to create the pool.  
- They then call the pool’s initialize() function with a sqrtPriceX96 value corresponding to a 1e18:1 price ratio in favor of WETH.  
4. Next, the attacker makes a purchase on the HotCurves contract, moving the internal market cap from 11.49 ETH to 11.51 ETH, surpassing the threshold and triggering finalize().  
5. Inside finalize(), the contract calls createAndInitializePoolIfNecessary(). This function checks if the pool already exists and is initialized. Since the attacker preemptively initialized it at an extreme price ratio, the function simply returns the existing pool without resetting the price.  
Reference: Uniswap V3 PoolInitializer.sol  
6. The contract then calls mintPosition() without slippage protection:  
amount0Min = 0;  
amount1Min = 0;  
As a result, the contract blindly deposits all its hotKey and Token into the already-skewed pool, providing liquidity at the attacker’s extreme rate of 1 Token per 1e18 hotKey.  
7. The attacker can now execute their profit-taking sequence:  
- First, they swap their Token holdings (obtained during step 4) for HotKey tokens in the newly created Uniswap V3 pool  
- Due to the skewed price ratio, this swap extracts a disproportionate amount of HotKey tokens from the pool  
- Finally, they swap the obtained HotKey tokens for WETH using the existing UniswapV2 and other UniswapV3 pools, resulting in a profitable ETH position

## Recommendation
To mitigate this attack, the following measures should be implemented:
1. Hard cap the market cap on the bonding curve, refunding the exceeding part of the last purchase to the buyer. The last buyToken() transaction should satisfy currentMarketCap = finalMarketCap so that the amount of liquidity that will be migrated to UniswapV3 is known in advance.
2. Since the amount of liquidity to be migrated is known in advance, the initial price ratio is known too. The factory, when creating new Coin and HotCurves contracts, should also front-run the initialization.
