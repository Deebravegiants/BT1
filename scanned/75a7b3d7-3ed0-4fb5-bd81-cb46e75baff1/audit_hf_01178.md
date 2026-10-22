# [C] Inconsistent Decimal Handling in Token Price Calculations

## Summary
Severity: Critical
Contest weight: 0.7817
Dataset id: 5055
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Agent contract performs multiple arithmetic operations for determining token purchase and sale amounts, specifically in the functions calculateAveragePrice, buyTokens, and calculateSellReturn. These calculations assume a uniform token decimal precision—implicitly expecting all payment tokens to use 18 decimals. This assumption breaks down when dealing with tokens like USDC (commonly 6 decimals on Ethereum), potentially leading to significant discrepancies in the computed values.  
For example, in calculateAveragePrice, the operation:  
```solidity
uint256 tokenAmount = (inputAmount * PRECISION) / estimatedPrice;
```  
does not take into account the inputAmount or tokenAmount token's decimals. Similarly, in buyTokens:  
```solidity
uint256 tokenAmount = (paymentAmount * PRECISION) / avgPrice;
```  
and in calculateSellReturn, the logic lacks decimal normalization for the involved ERC20 tokens.  
Without adjusting for varying token decimals, token valuations will be inaccurate, creating opportunities for exploitation (e.g., buying underpriced tokens or overpaying) or leading to unexpected contract behavior.

Impact Explanation:  
High, because incorrect decimal handling can lead to severe financial discrepancies.  
Buyers may receive fewer tokens than expected, and sellers may receive more or less than deserved.  
This not only affects user trust but could also be exploited for arbitrage or manipulation, especially with tokens of different decimal formats. Additionally, errors in fund calculation could result in long-term fund imbalances within the protocol's treasury or reserve pool.

## Recommendation
Introduce a decimal normalization mechanism that accounts for the decimals of the payment token and the token being bought or sold. This can be achieved by querying the decimals() function of each ERC20 token and applying an appropriate scaling factor during calculations. Alternatively, enforce that all supported payment tokens must conform to 18 decimals and reject any tokens with different configurations.  
A more flexible and robust design would involve explicitly scaling inputAmount and paymentAmount to a common 18-decimal standard during computation and scaling the final tokenAmount result back to the token’s actual decimal precision. This ensures mathematical correctness and prevents rounding or overflow errors due to mismatched assumptions.
