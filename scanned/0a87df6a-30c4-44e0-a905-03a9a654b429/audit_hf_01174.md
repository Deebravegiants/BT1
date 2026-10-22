# [M] Donation attack using paymentToken affects intended protocol behavior

## Summary
Severity: Medium
Contest weight: 0.5907
Dataset id: 5045
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
By donation of the amount minMarketCapThreshold of paymentToken to the Agent contract, the isMarketCapReached method can be manipulated to return true before any agent tokens are sold:  
```solidity
function isMarketCapReached() public view returns (bool) {
    return paymentToken.balanceOf(address(this)) >= minMarketCapThreshold;
}
```  
This in turn, allows an adversary to trigger LP creation and subsequently disable future buy-ins (be the only buyer) by performing only one small buy-in:  
```solidity
function buyTokens(uint256 amount) external nonReentrant returns (uint256) {
    require(amount > 0, "Amount must be greater than 0");
    require(!isLPCreated, "Bonding curve phase ended");
    // ...
    // Create LP if conditions are met
    if (automaticLPCreation && !isLPCreated && isMarketCapReached()) {
        createLPPosition();
    }
    // ...
}
```  
Afterwards, the remaining amount of agent tokens in the contract will be inflated (way higher than intended) due to cutting ahead of the bonding curve, i.e. not selling as many agent tokens as intended.  
As a consequence:  
• The lpTokenAmount of agent tokens at LP creation will be inflated, leading to a devalued pool price.  
• The contribAmount on token distribution will be inflated and is fully transferred to the adversary (if they manage to be the only buyer using this attack vector).

Impact Explanation:  
Medium:  
• Circumvents permissioned manualCreateLP method, cutting ahead of the bonding curve permissionlessly.  
• Remaining tokens for distribution and LP creation are inflated because only a small amount of agent tokens is sold before LP creation.  
• An adversary can get the whole inflated contributor distribution amount for just a small buy-in.  
• LP price is lower than intended due to inflated agent token amount at LP creation.  
• Generally tampers with expected and intended protocol behavior.

## Recommendation
It is recommended to rely on internal accounting of the paymentToken balance instead of using balanceOf to avoid manipulation of the isMarketCapReached method.
