# [C] The granularity of 1M tokens for buy and sell operations in the BondingCurve contract leads to user fund losses

## Summary
Severity: Critical
Contest weight: 0.9769
Dataset id: 4191
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The current implementation contains significant flaws that disrupt the system and cause substantial losses for users. These issues arise because the calculations for buy and sell amounts are truncated to full millions of tokens.
In the buy() function, when a user transfers ETH to buy tokens, if the resulting amount of tokens for a given trade is, for example, 1.9M tokens, the user will still pay as if he is receiving 1.9M tokens but will only receive 1M. This results in a loss of approximately 47%.
```solidity
uint256 actualTokens = (tokensToTransfer / 1e18) * 1_000_000 * 1e18;
```
In the sell() function, if a user transfers 1.9M tokens to sell, he will only be refunded ETH equivalent to 1M tokens, but the entire 1.9M tokens will be transferred to the contract. This results in a similar 47% loss. Furthermore, incorrect deduction of the internal n virtual accounting value, used for bonding curve calculations, leads to inaccurate stored values, which inflates the token price.
```solidity
uint256 newN = n - (tokenAmount / (1_000_000)); // <-- truncation
uint256 currentETH = ethForN(n);
uint256 newETH = ethForN(newN);
uint256 refundETH = currentETH - newETH;

require(
    tokenContract.transferFrom(msg.sender, address(this), tokenAmount),
    "Token transfer failed"
);
```
```solidity
function ethForN(uint256 n_) public pure returns (uint256) {
    uint256 n_value = n_ / 1e18; // <-- truncation
```
This issue stems from the ethForN() function, where the bonding curve is implemented as a step function that calculates values per million tokens. The decision to use cubic calculations in the bonding curve introduced complications, and to avoid overflows, the calculations were restricted to per-million token steps, which impacts both the linear and cubic parts of the equation.

## Recommendation
While there is no simple solution for cubic calculations, the bonding curve can be updated to better align with expected calculations and business requirements. The curve can be smoothed by implementing a linear function with a granularity of 1 wei and a cubic part with a granularity of 1e6, instead of the current 1e24 granularity for both parts.
Update the ethForN() function as follows:
```solidity
function ethForN(uint256 n_) public pure returns (uint256) {
    uint256 linear = (P0 * n_) / 1e18;
    uint256 cubic = (A * ((n_ / 1e6) ** 3)) / 1e54;
    return linear + cubic;
}
```
Where P0 is 5e9 and A is 60e9.
In addition to updating ethForN(), make the following adjustments to ensure consistency with the updated bonding curve:
- In solveForN(), use uint256 high = MAX_MILLION_TOKENS * 1e24.
- Remove adjustments to millions in the buy() and sell() functions.
- Update the old require:
```solidity
require(newN <= MAX_MILLION_TOKENS * 1e18, "Max token supply reached");
```
and adjust it to correctly check for 500M tokens.
