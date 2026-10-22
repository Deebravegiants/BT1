# [M] VLT-4 | Invalid Flagship LST Amount Transferred In

## Summary
Severity: Medium
Contest weight: 0.1274
Dataset id: 20591
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the deposit(uint256 assets, address _receiver) function the assets amount passed to the super.deposit function is an ether value of the flagship asset amount. However the ERC4626 deposit function will transfer in the ether value amount of the flagship asset rather than the flagship asset amount. The value of the amount transferred in is correctly converted to shares as the previewDeposit function is correctly overridden in the Vault contract, however the user still transfers in an unexpected amount of the flagship asset. Consider the following example: - Flagship asset price is 0.8 ether - Bob calls deposit(1 * 1e18, address(bob)) - The vault transfers 0.8 * 1e18 of the flagship asset from Bob This is unexpected for Bob as he specified 1 * 1e18 of the flagship asset to be transferred in.

## Recommendation
Do not convert the specified assets amount to an ether amount in the deposit(uint256 assets, address receiver) function, as this conversion is already accounted for in the previewDeposit function.
