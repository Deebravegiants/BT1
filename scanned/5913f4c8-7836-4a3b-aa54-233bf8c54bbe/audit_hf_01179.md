# [H] Anyone can preliminarily create an agent's Uniswap pair leading to stuck payment tokens

## Summary
Severity: High
Contest weight: 0.3389
Dataset id: 5056
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The createLPPosition method of the Agent contract intends to create a Uniswap pair (agentToken/paymentToken) with an asset ratio (price) according to the specified amounts lpTokenAmount/lpPaymentAmount. However, the method expects the Uniswap pair not to exist yet and subsequently expects the full amounts to be utilized, leading to a price that should approximately match the last valuation of the bonding curve.  
In case the Uniswap pair was externally created beforehand, Uniswap's addLiquidity method will maintain the present asset ratio (price). Consequently, the desired amounts lpTokenAmount/lpPaymentAmount are unlikely to be fully utilized, and the expected liquidity tokens are unlikely to be minted.  
Attack path:  
1. The adversary buys some agent tokens. Preferably shortly after deployment of the agent to secure a better entry price.  
2. The adversary creates the LP with a high agent to payment token ratio to set a low price for agent tokens. Preferably this is done shortly before the agent attempts to create the LP.  
3. The agent attempts to create the LP and add liquidity. Thereby, the agent to payment token ratio will be maintained leading to payment tokens being left over and stuck in the agent contract.  
4. The adversary can buy the severely underpriced agent tokens from the LP.

Impact Explanation:  
High:  
• Any paymentToken not used by addLiquidity due to the asset ratio will be stuck/lost in the Agent contract.  
• The Uniswap pair's price does not match the last valuation according to the bonding curve.  
• Severely underpriced payment tokens can be bought from the Uniswap pair.

## Recommendation
It is recommended to restrict transfers of the AgentToken to/from the deterministic address of the Uniswap pair (agentToken/paymentToken) until activated in the createLPPosition method. This way, no one can preliminarily create the pair and set the price.
