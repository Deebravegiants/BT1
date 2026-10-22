# [H] An off-by-one error leads to stuck funds and unexpected errors

## Summary
Severity: High
Contest weight: 0.5731
Dataset id: 8424
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The use of a wrong comparison operator will make it impossible to withdraw the whole balance of the contract:
```solidity
function withdraw(uint256 amount) external onlyOwner {
    require(amount > 0, "withdraw amount is zero");
    emit Withdrawn(amount);
    (bool sent, ) = payable(msg.sender).call{value: amount}("");
    require(sent, "ether withdraw failed");
}
```
As it can be seen from the second require statement, the amount should be strictly less than to get the native tokens out of the contract.
The same issue is present in the onERC721Received, onERC1155Received and onERC1155BatchReceived functions where it is required the balance of the contract to be strictly more than the offer:
This means that even if there is enough tokens in the contracts to buy the users' tokens, the call will revert with an error message. This could be quite frustrating for users. For example, if the offer is 0.0001 ether and there is the exact amount, the call will revert.

## Recommendation
GarageSale_report.md
Change the above instances to >= and <=.
