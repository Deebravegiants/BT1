# [M] UniswapV3DecoderAndSanitizer allows strategies to drain the vault through providing malicious positions on UniV3

## Summary
Severity: Medium
Contest weight: 0.1978
Dataset id: 6031
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The UniswapV3DecoderAndSanitizer supports two methods for providing liquidity. The first is through mint, where the provided tokens are checked. The second is through increaseLiquidity, where it verifies that the owner of the position is the boringVault. However, this validation is not sufficient to prevent malicious strategies from draining the boringVault  
• For increaseLiquidity, since the increaseLiquidity function only verifies that the owner of the current position is the boringVault, an exploiter can send a malicious UniswapV3 position to the boringVault and trigger increaseLiquidity to have the boringVault provide liquidity to the malicious position, thereby enabling the exploiter to profit.  
For example, let's assume the base token of the Vault is USDT. The exploiter can first create a fake token, FAKE, and establish a FAKE-USDT market on UniswapV3. By sending a dust position of FAKE-USDT to the boringVault, the UniswapV3DecoderAndSanitizer would consider it a valid position and proceed to provide liquidity to the FAKE-USDT market. The exploiter can then profit by buying all USDT on the FAKE-USDT market.  
• For mint, since the UniswapV3DecoderAndSanitizer only checks the tokens of the market. The malicious strategy can provide liquidity at a malicious tick. Providing liquidity at a malicious tick is similar to selling tokens at a really bad price. It creates a arbitrage space for the exploiter to further take profit by selling tokens on the market.

## Recommendation
Consider validating the tick, fee, and token when providing liquidity to Uniswap V3 markets.
