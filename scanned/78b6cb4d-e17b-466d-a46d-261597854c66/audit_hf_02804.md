# [M] Vault.withdrawServiceFee() should reset totalServiceToken and totalServiceEth.

## Summary
Severity: Medium
Contest weight: 0.4198
Dataset id: 15254
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Vault.withdrawServiceFee() is supposed to transfer the accumulated fees to an address specified by the owner. The issue is that totalServiceToken and totalServiceEth are not reset back to 0. Firstly, this gives the owner full control over the Vault's funds since he can repeatedly call Vault.withdrawServiceFee() and drain the funds. Secondly, assuming a non-malicious owner, there could be a scenario where Vault.withdrawServiceFee() is called once during the Vault being active and once after the Vault has expired and users have withdrawn. In such a scenario, Vault.withdrawServiceFee() will revert unexpectedly the second time it has been called since the already withdrawn fee will still be accounted for in totalServiceToken and totalServiceEth.
```solidity
function withdrawServiceFee(address payable withdrawAddress) external onlyOwner {
underwritingToken.transfer(withdrawAddress, vaultStorage.state.totalServiceToken);
withdrawAddress.call{value: vaultStorage.state.totalServiceEth}("");
}
```

## Recommendation
```diff
@@ -364,8 +365,12 @@ contract Vault is
function withdrawServiceFee(address payable withdrawAddress) external onlyOwner {
underwritingToken.transfer(withdrawAddress, vaultStorage.state.totalServiceToken);
withdrawAddress.call{value: vaultStorage.state.totalServiceEth}("");
+
uint256 amountOfEth = vaultStorage.state.totalServiceEth;
+
uint256 amountOfToken = vaultStorage.state.totalServiceToken;
+
vaultStorage.state.totalServiceEth = 0;
+
vaultStorage.state.totalServiceToken = 0;
+
underwritingToken.transfer(withdrawAddress, amountOfToken);
+
withdrawAddress.call{value: amountOfEth}("");
}
```
