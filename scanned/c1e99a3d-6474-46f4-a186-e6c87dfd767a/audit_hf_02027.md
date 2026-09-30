# [H] Improper Logic Of withdrawFunds()

## Summary
Severity: High
Contest weight: 0.7561
Dataset id: 11562
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
According to the 2CrazyNFT design, the TwoCrazy contract will likely accumulate a huge amount of assets with the increased transactions through buyNFT(), while the privileged EDITOR_ROLE account has capability to withdraw the assets with the calling of withdrawFunds(). While examining the logic of the withdrawFunds() routine, we observe there is an improper implementation that needs to be improved. To elaborate, we show below the related code snippet of the withdrawFunds() routine. In the withdrawFunds() routine, we notice ERC20(feeToken).transferFrom(address(this), msg.sender, feesCollected[feeToken]) is called to transfer the feeToken locked in address(this) to msg.sender. This is reasonable under the assumption that the transferFrom()’s implementation of feeToken supports the user spends his/her own token without approval. Otherwise, the feeToken locked in the TwoCrazy contract will be lost forever.
```solidity
function withdrawFunds(address feeToken) public payable onlyRole(EDITOR_ROLE) {
    ERC20(feeToken).transferFrom(address(this), msg.sender, feesCollected[feeToken]);
    feesCollected[feeToken] = 0;
}
```

## Recommendation
Correct the implementation of the withdrawFunds() routine as below.
```solidity
function withdrawFunds(address feeToken) public payable onlyRole(EDITOR_ROLE) {
    uint256 collectedFees = feesCollected[feeToken];
    feesCollected[feeToken] = 0;
    ERC20(feeToken).safeTransfer(msg.sender, collectedFees);
}
```
