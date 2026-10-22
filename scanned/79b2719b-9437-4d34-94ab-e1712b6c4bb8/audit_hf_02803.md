# [M] In Vault.purchase() the denomination of premium is ambiguous

## Summary
Severity: Medium
Contest weight: 0.4112
Dataset id: 15253
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Purchasing coverage requires the user to pay an agreed premium for the coverage that he will receive for the given node. The issue is that it's not clear if the premium is denominated in native ETH or in underwritingToken (Assumed to be wstETH). If the premium is agreed upon to be in ETH, then the user cannot pay in underwritingToken since the price of wstETH is higher than ETH and the user will lose out on funds. If the premium is agreed upon to be in wstETH then the user can choose to pay the same amount of premium but in native ETH, thus receiving an unfair discount.
# Vault.sol
```solidity
function purchase(
uint256 premium,
) external payable nonReentrant onlyNonZero(premium) WhenNotPaused WhenVaultNotExpired {
validatePurchaseParams(
riskScore,
premium,
);
bool paidInEth = true;
if (msg.value < premium) {
underwritingToken.transferFrom(msg.sender, address(this), premium);
paidInEth = false;
}
if (paidInEth && msg.value > premium) {
msg.sender.call{value: (msg.value - premium)}("");
}
```

## Recommendation
The denomination of premium that's used in the off-chain components should be assumed and the conversion rate supplied in convertToEthFactor should be used to convert premium either in underwritingToken or native ETH.
