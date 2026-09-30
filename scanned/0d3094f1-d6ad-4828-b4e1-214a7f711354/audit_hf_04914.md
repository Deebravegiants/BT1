# [M] Potential ETH Loss Due to transfer Usage in

## Summary
Severity: Medium
Contest weight: 0.5905
Dataset id: 22833
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
• The Requestor contract uses transfer to send ETH which has the risk that it will not work if the gas cost increases/decrease(low Likelihood), but it is highly likely to fail on zkSync due to gas limits. This may make users' ETH irretrievable.
• Users (or bots) interact with RngWitnet to request a random number and start a draw in the DrawManager contract. To generate a random number, users must provide some ETH that will be sent to WitnetRandomness to generate the random number.
```solidity
function startDraw(uint256 rngPaymentAmount, DrawManager _drawManager, address _rewardRecipient) external payable returns (uint24) {
    (uint32 requestId,,) = requestRandomNumber(rngPaymentAmount);
    return _drawManager.startDraw(_rewardRecipient, requestId);
}
```
• The ETH sent with the transaction may or may not be used (if there is already a request in the same block, it won't be used). Any remaining or unused ETH will be sent to Requestor, so the user can withdraw it later.
• The issue is that the withdraw function in the Requestor contract uses transfer to send ETH to the receiver. This may lead to users being unable to withdraw their funds.
```solidity
function withdraw(address payable _to) external onlyCreator returns (uint256) {
    uint256 balance = address(this).balance;
    _to.transfer(balance);
    return balance;
}
```
• The protocol will be deployed on different chains including zkSync, on zkSync the use of transfer can lead to issues, as seen with won't be anough in some cases even to send eth to an EOA, It is explicitly mentioned in their docs to not use the transfer method to send ETH here.
notice that in case msg.sender is a contract that have some logic on it's receive or fallback function the ETH is definitely not retrievable. since this contract can only withdraw eth to it's own addres which will always revert.
• Draw Bots' ETH may be irretrievable or undelivered, especially on zkSync, due to the use of .transfer.

## Recommendation
• recommendation to use .call() for ETH transfer.
